"""SQLite persistence: WAL, separate per-request connections, prepared SQL, audited writes."""
from __future__ import annotations
import json, os, sqlite3, hashlib, secrets, datetime, pathlib, threading
from contextlib import contextmanager

UTC=datetime.timezone.utc

def now(): return datetime.datetime.now(UTC).isoformat(timespec='seconds')
def uid(prefix): return prefix+'-'+secrets.token_hex(7).upper()
def data_dir():
    d=pathlib.Path(os.getenv('CSC_DATA_DIR',str(pathlib.Path(__file__).resolve().parents[1]/'data'))).resolve()
    d.mkdir(parents=True,exist_ok=True)
    return d

def path(): return data_dir()/'cscms.sqlite3'

@contextmanager
def connect():
    conn=sqlite3.connect(str(path()),timeout=10,isolation_level=None,check_same_thread=False)
    conn.row_factory=sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=10000')
    try: yield conn
    finally: conn.close()

def init_db():
    with connect() as c:
        c.executescript('''
CREATE TABLE IF NOT EXISTS users (
 id TEXT PRIMARY KEY,username TEXT UNIQUE NOT NULL COLLATE NOCASE,display_name TEXT NOT NULL,
 email TEXT,role TEXT NOT NULL,unit TEXT NOT NULL DEFAULT '',password_hash TEXT NOT NULL,
 must_change INTEGER NOT NULL DEFAULT 1,active INTEGER NOT NULL DEFAULT 1,
 failed_attempts INTEGER NOT NULL DEFAULT 0,locked_until TEXT,
 created_at TEXT NOT NULL,updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
 token_hash TEXT PRIMARY KEY,user_id TEXT NOT NULL,csrf_token TEXT NOT NULL,
 expires_at TEXT NOT NULL,created_at TEXT NOT NULL,
 FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
CREATE TABLE IF NOT EXISTS records (
 id TEXT PRIMARY KEY,kind TEXT NOT NULL,unit TEXT NOT NULL DEFAULT '',
 data_json TEXT NOT NULL,created_by TEXT NOT NULL,created_at TEXT NOT NULL,
 updated_at TEXT NOT NULL,version INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_record_kind_unit ON records(kind,unit);
CREATE TABLE IF NOT EXISTS evidence_files (
 id TEXT PRIMARY KEY,task_id TEXT NOT NULL,uploader_id TEXT NOT NULL,
 original_name TEXT NOT NULL,mime_type TEXT NOT NULL,size_bytes INTEGER NOT NULL,
 sha256 TEXT NOT NULL,stored_name TEXT NOT NULL,drive_id TEXT,
 created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_evidence_task ON evidence_files(task_id);
CREATE TABLE IF NOT EXISTS audit (
 id TEXT PRIMARY KEY,at TEXT NOT NULL,actor_id TEXT,actor_role TEXT NOT NULL,
 action TEXT NOT NULL,kind TEXT NOT NULL,record_id TEXT NOT NULL,
 before_hash TEXT,after_hash TEXT,details TEXT
);
CREATE INDEX IF NOT EXISTS idx_audit_when ON audit(at);
CREATE TABLE IF NOT EXISTS sync_queue (
 id TEXT PRIMARY KEY,kind TEXT NOT NULL,record_id TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'pending',tries INTEGER NOT NULL DEFAULT 0,
 last_error TEXT,queued_at TEXT NOT NULL,synced_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_sync_pending ON sync_queue(status,queued_at);
CREATE TABLE IF NOT EXISTS settings (name TEXT PRIMARY KEY,value TEXT NOT NULL,updated_at TEXT NOT NULL);
''')
        if not c.execute("SELECT 1 FROM settings WHERE name='schema_version'").fetchone():
            c.execute('INSERT INTO settings VALUES(?,?,?)',('schema_version','1',now()))

def obj_row(r):
    if not r:return None
    data=json.loads(r['data_json'])
    data.update(id=r['id'],kind=r['kind'],unit=r['unit'],created_at=r['created_at'],updated_at=r['updated_at'],version=r['version'])
    return data

def get_record(c,kind,rid):
    return obj_row(c.execute('SELECT * FROM records WHERE kind=? AND id=?',(kind,rid)).fetchone())

def list_records(c,kind):
    return [obj_row(r) for r in c.execute('SELECT * FROM records WHERE kind=? ORDER BY updated_at DESC LIMIT 1500',(kind,)).fetchall()]

def save_record(c,kind,rid,unit,body,actor,version=None):
    old=get_record(c,kind,rid); stamp=now()
    d={k:v for k,v in body.items() if k not in ('kind','id','unit','created_at','updated_at','version','created_by')}
    if old:
        if version is None or old['version']!=version: raise ValueError('VERSION_CONFLICT')
        old_body={k:v for k,v in old.items() if k not in ('kind','id','unit','created_at','updated_at','version')}
        merged={**old_body,**d}
        c.execute('UPDATE records SET data_json=?,unit=?,version=version+1,updated_at=? WHERE id=? AND kind=?',
                  (json.dumps(merged,ensure_ascii=False),unit,stamp,rid,kind))
    else:
        c.execute('INSERT INTO records VALUES(?,?,?,?,?,?,?,?)',(rid,kind,unit,json.dumps(d,ensure_ascii=False),actor,stamp,stamp,1))
    new=get_record(c,kind,rid)
    audit(c,actor,'create' if not old else 'update',kind,rid,old,new)
    queue(c,kind,rid)
    return new

def sha(data):
    return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False,default=str).encode()).hexdigest() if data is not None else None

def audit(c,actor,action,kind,rid,before=None,after=None,details=''):
    row=c.execute('SELECT role FROM users WHERE id=?',(actor,)).fetchone() if actor else None
    role=row['role'] if row else 'system'
    c.execute('INSERT INTO audit VALUES(?,?,?,?,?,?,?,?,?,?)',(uid('AUD'),now(),actor,role,action,kind,rid,sha(before),sha(after),str(details)[:900]))
    queue(c,'audit',c.execute('SELECT id FROM audit ORDER BY rowid DESC LIMIT 1').fetchone()['id'])

def queue(c,kind,rid):
    c.execute('INSERT INTO sync_queue VALUES(?,?,?,?,?,?,?,?)',(uid('SYNC'),kind,rid,'pending',0,None,now(),None))

def db_backup(dest):
    with connect() as src:
        target=sqlite3.connect(str(dest))
        try: src.backup(target)
        finally: target.close()
