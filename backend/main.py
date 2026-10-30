"""CSC-MS Portal — FastAPI backend. Real auth, RBAC, persistence, evidence and audit.
Service owns an SQLite database; optional verified Google Sheets/Drive synchronization.
"""
from __future__ import annotations
import os,re,json,secrets,hashlib,mimetypes,datetime,pathlib,logging,threading,time
from zoneinfo import ZoneInfo
from typing import Any
from fastapi import FastAPI,Request,Response,HTTPException,Depends,UploadFile,File,Form
from fastapi.responses import FileResponse,StreamingResponse,HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel,Field
from .database import init_db,connect,now,uid,data_dir,get_record,list_records,save_record,audit,queue
from .security import hasher,hash_password,verify_password,password_ok,safe_user,session_hash,create_session,read_session,require_admin,is_scope,can_read,can_create,can_update,ALLOWED_ROLES
from . import google_sync

BASE=pathlib.Path(__file__).resolve().parents[1]
WEB=BASE/'web'
ENV=os.getenv('CSC_ENV','development').lower()
PRODUCTION=ENV=='production'
COOKIE_SECURE=os.getenv('CSC_COOKIE_SECURE', '1' if PRODUCTION else '0')=='1'
MAX_UPLOAD_BYTES=int(os.getenv('CSC_MAX_UPLOAD_MB','50'))*1024*1024
UPLOAD_EXT={'.pdf','application/pdf','.jpg','image/jpeg','.jpeg','.png','image/png','.webp','image/webp','.mp4','video/mp4','.mov','video/quicktime','.docx','application/vnd.openxmlformats-officedocument.wordprocessingml.document','.xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}
KINDS={'student','scholarship','event','campaign','task','attendance','referral','exemption','annual_review','approval','sop','weekly_score','taiwan_application'}
FIELDS={
'student':{'nim','name','program','cohort','email','status','notes'},
'scholarship':{'student_id','academic_year','tier','start_date','end_date','status','sk_number'},
'event':{'name','category','objective','date','end_date','pic','status','target_attendees','attendees','budget','proposal_file_id','report_file_id','notes'},
'campaign':{'name','month','pic','message','audience','target','delivered','status','notes'},
'task':{'student_id','category','title','brief','target','acceptance_criteria','date','due_date','pic','status','campaign_id','event_id','review_score','review_note','reviewed_by','reviewed_at'},
'attendance':{'student_id','task_id','date','status','reason','approval_id','notes'},
'referral':{'referrer_student_id','new_student_name','new_student_id','admission_record_id','status','payment_status','pm_verified_at','pm_verified_by','finance_verified_at','finance_verified_by','attribution_note','used_for','notes'},
'exemption':{'student_id','referral_id','exemption_type','start_date','end_date','status','approved_at','approved_by','notes'},
'annual_review':{'student_id','academic_year','contribution_score','academic_score','character_score','total_score','gpa','requested_tier','recommended_tier','final_tier','status','decision_note','rector_approved_at'},
'approval':{'record_type','record_id','title','status','decision','decision_note','requested_by','decided_by','decided_at'},
'sop':{'title','sop_version','status','file_id','effective_date','summary'},
'weekly_score':{'task_id','student_id','reviewer_id','quality_0_5','target_0_5','timeliness_0_5','initiative_0_5','teamwork_0_5','weighted_score','result_status','review_note','reviewed_at'},
'taiwan_application':{'student_id','partner','program_type','contribution_path','referral_id','alternative_task_id','gpa','language_level','academics_confirmed','partner_requirements_confirmed','notes','status','approved_by','approved_at','approved_dual_use'},
}
READ_ONLY_FIELDS={
'referral':{'pm_verified_at','pm_verified_by','finance_verified_at','finance_verified_by','payment_status','status','used_for'},
'exemption':{'approved_at','approved_by','start_date','end_date','status'},
'annual_review':{'final_tier','rector_approved_at'},
'task':{'review_score','review_note','reviewed_at','reviewed_by'},
'approval':{'decision','decision_note','decided_by','decided_at','status'},
'taiwan_application':{'status','approved_by','approved_at','approved_dual_use'},
'weekly_score':{'task_id','student_id','reviewer_id','quality_0_5','target_0_5','timeliness_0_5','initiative_0_5','teamwork_0_5','weighted_score','result_status','review_note','reviewed_at'},
}
app=FastAPI(title='Carnegie Scholarship & Activity Portal',docs_url=None,redoc_url=None,openapi_url=None)
app.mount('/assets',StaticFiles(directory=WEB/'assets'),name='assets')

@app.on_event('startup')
def startup():
    init_db()
    if PRODUCTION:
        with connect() as c:
            weak_admins=c.execute("SELECT username,password_hash FROM users WHERE role='admin' AND active=1 AND must_change=1").fetchall()
            if any(verify_password('123456',x['password_hash']) for x in weak_admins):
                raise RuntimeError('SECURITY STOP: Admin menggunakan 123456. Ganti password pada setup lokal sebelum deployment.')
    logging.getLogger('cscms').info('CSC-MS started in %s mode',ENV)
    if os.getenv('GOOGLE_SYNC_AUTOMATIC','1')=='1':
        def run_sync():
            while True:
                time.sleep(90)
                try:
                    if google_sync.config()['configured']:
                        google_sync.sync_queue(max_items=60)
                except Exception:
                    logging.getLogger('cscms').exception('Background Google sync failed; queue remains pending')
        threading.Thread(target=run_sync,daemon=True,name='cscms-google-sync').start()

@app.middleware('http')
async def security_headers(req:Request,call_next):
    res=await call_next(req)
    for k,v in {'X-Content-Type-Options':'nosniff','X-Frame-Options':'DENY','Referrer-Policy':'no-referrer',
                'Permissions-Policy':'camera=(), microphone=(), geolocation=()',
                'Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"}.items():res.headers[k]=v
    if PRODUCTION:res.headers['Strict-Transport-Security']='max-age=31536000; includeSubDomains'
    if req.url.path.startswith('/api/') or req.url.path=='/login':res.headers['Cache-Control']='no-store'
    return res

@app.get('/',response_class=HTMLResponse)
def index():return (WEB/'index.html').read_text('utf8')
@app.get('/health')
def health():return {'status':'ok','service':'CSC-MS WEB','environment':ENV}

class Login(BaseModel):
    username:str=Field(min_length=2,max_length=60)
    password:str=Field(min_length=1,max_length=128)
class ChangePassword(BaseModel):
    old_password:str
    new_password:str
class NewUser(BaseModel):
    username:str=Field(min_length=3,max_length=40)
    display_name:str=Field(min_length=2,max_length=80)
    role:str
    unit:str=''
    email:str=''
class UpdateUser(BaseModel):
    display_name:str|None=None
    role:str|None=None
    unit:str|None=None
    active:bool|None=None
class RecordPayload(BaseModel):
    unit:str=''
    data:dict[str,Any]
class PatchPayload(BaseModel):
    version:int
    data:dict[str,Any]
class ReviewPayload(BaseModel):
    version:int
    quality:int=Field(ge=0,le=5)
    target:int=Field(ge=0,le=5)
    timeliness:int=Field(ge=0,le=5)
    initiative:int=Field(ge=0,le=5)
    teamwork:int=Field(ge=0,le=5)
    decision:str
    note:str=''
class VerifyPayload(BaseModel):
    version:int
    verified:bool
    reference_note:str=''
class ExemptionPayload(BaseModel):
    version:int
    approve:bool
    note:str=''
class TaiwanDecisionPayload(BaseModel):
    version:int
    approve:bool
    allow_dual_use:bool=False
    note:str=''

class AnnualDecisionPayload(BaseModel):
    version:int
    approve:bool
    final_tier:int|None=None
    note:str=''


def auth(req:Request):
    token=req.cookies.get('csc_session')
    with connect() as c:
        u=read_session(c,token)
        if not u:raise HTTPException(401,'Sesi habis. Silakan masuk kembali.')
        # Limit changing initial password to only /me, /change-password and /logout.
        if u['must_change'] and req.url.path not in ('/api/me','/api/auth/change-password','/api/auth/logout'):
            raise HTTPException(403,'Wajib mengganti password sementara terlebih dahulu.')
        if req.method in ('POST','PUT','PATCH','DELETE'):
            if not secrets.compare_digest(req.headers.get('X-CSRF-Token',''),u['csrf_token']):
                raise HTTPException(403,'CSRF token tidak cocok.')
        return dict(u)

def set_cookie(res,token):
    res.set_cookie('csc_session',token,httponly=True,secure=COOKIE_SECURE,samesite='lax',path='/',max_age=36000)

def csrf_response(u):return {'user':safe_user(u),'csrf':u['csrf_token']}

@app.post('/api/auth/login')
def login(body:Login,response:Response):
    with connect() as c:
        u=c.execute('SELECT * FROM users WHERE username=? COLLATE NOCASE',(body.username.strip(),)).fetchone()
        if u and u['locked_until'] and u['locked_until']>now():raise HTTPException(429,'Akun terkunci sementara. Coba beberapa saat lagi.')
        if not u or not u['active'] or not verify_password(body.password,u['password_hash']):
            if u:
                fails=u['failed_attempts']+1
                locked=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(minutes=15)).isoformat(timespec='seconds') if fails>=5 else None
                c.execute('UPDATE users SET failed_attempts=?,locked_until=? WHERE id=?',(fails,locked,u['id']))
            raise HTTPException(401,'Username atau password tidak sesuai.')
        c.execute('UPDATE users SET failed_attempts=0,locked_until=NULL WHERE id=?',(u['id'],))
        c.execute('DELETE FROM sessions WHERE user_id=?',(u['id'],))
        token,csrf=create_session(c,u)
        set_cookie(response,token)
        return {'user':safe_user(u),'csrf':csrf,'must_change':bool(u['must_change'])}

@app.get('/api/me')
def me(u=Depends(auth)):return csrf_response(u)

@app.post('/api/auth/logout')
def logout(response:Response,req:Request,u=Depends(auth)):
    with connect() as c:c.execute('DELETE FROM sessions WHERE token_hash=?',(session_hash(req.cookies.get('csc_session','')),))
    response.delete_cookie('csc_session',path='/')
    return {'ok':True}

@app.post('/api/auth/change-password')
def change_password(body:ChangePassword,response:Response,u=Depends(auth)):
    if not verify_password(body.old_password,u['password_hash']):raise HTTPException(401,'Password lama salah.')
    if not password_ok(body.new_password):raise HTTPException(400,'Password baru minimal 12 karakter, gabungan tiga jenis: besar, kecil, angka, simbol.')
    if body.old_password==body.new_password:raise HTTPException(400,'Password baru harus berbeda.')
    with connect() as c:
        c.execute('UPDATE users SET password_hash=?,must_change=0,failed_attempts=0,locked_until=NULL,updated_at=? WHERE id=?',
                  (hash_password(body.new_password),now(),u['id']))
        c.execute('DELETE FROM sessions WHERE user_id=?',(u['id'],))
        audit(c,u['id'],'change_password','user',u['id'])
    response.delete_cookie('csc_session',path='/')
    return {'ok':True,'message':'Password berhasil diganti. Masuk kembali menggunakan password baru.'}

@app.get('/api/users')
def list_users(u=Depends(auth)):
    require_admin(u)
    with connect() as c:return {'items':[safe_user(x) for x in c.execute('SELECT * FROM users ORDER BY created_at DESC')]}

@app.post('/api/users')
def create_user(body:NewUser,u=Depends(auth)):
    require_admin(u)
    role=body.role.lower()
    if role not in ALLOWED_ROLES:raise HTTPException(400,'Role tidak valid.')
    if not re.fullmatch(r'[A-Za-z0-9._-]{3,40}',body.username):raise HTTPException(400,'Username hanya huruf, angka, titik, underscore, atau minus.')
    if role in ('operator','reviewer') and body.unit not in ('WR I','WR II','WR III'):
        raise HTTPException(400,'Operator/reviewer wajib mempunyai unit.')
    temp=secrets.token_urlsafe(20)+'Z9!'
    user_id=uid('USR')
    try:
        with connect() as c:
            c.execute('INSERT INTO users VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
                      (user_id,body.username,body.display_name,body.email,role,body.unit,hash_password(temp),1,1,0,None,now(),now()))
            audit(c,u['id'],'create_user','user',user_id,details='created temp account')
    except Exception as e:
        if 'UNIQUE constraint' in str(e):raise HTTPException(409,'Username sudah digunakan.')
        raise
    return {'user_id':user_id,'username':body.username,'temporary_password':temp,'must_change':True,
            'message':'Bagikan password sekali melalui kanal aman. Tidak akan ditampilkan kembali.'}

@app.patch('/api/users/{user_id}')
def edit_user(user_id:str,body:UpdateUser,u=Depends(auth)):
    require_admin(u)
    with connect() as c:
        target=c.execute('SELECT * FROM users WHERE id=?',(user_id,)).fetchone()
        if not target:raise HTTPException(404,'User tidak ditemukan.')
        newrole=body.role or target['role']
        if newrole not in ALLOWED_ROLES:raise HTTPException(400,'Role tidak valid')
        active=target['active'] if body.active is None else int(body.active)
        if user_id==u['id'] and (not active or newrole!='admin'):
            raise HTTPException(400,'Tidak boleh menonaktifkan atau menurunkan role akun sendiri.')
        if target['role']=='admin' and (newrole!='admin' or not active):
            count=c.execute("SELECT count(*) as n FROM users WHERE role='admin' AND active=1").fetchone()['n']
            if count<2:raise HTTPException(400,'Admin aktif terakhir tidak boleh dinonaktifkan.')
        c.execute('UPDATE users SET display_name=?,role=?,unit=?,active=?,updated_at=? WHERE id=?',
                  (body.display_name or target['display_name'],newrole,body.unit if body.unit is not None else target['unit'],active,now(),user_id))
        c.execute('DELETE FROM sessions WHERE user_id=?',(user_id,))
        audit(c,u['id'],'edit_user','user',user_id,details='role or active updated')
    return {'ok':True}

@app.post('/api/users/{user_id}/reset-password')
def reset_password(user_id:str,u=Depends(auth)):
    require_admin(u)
    temp=secrets.token_urlsafe(20)+'P9!'
    with connect() as c:
        target=c.execute('SELECT id FROM users WHERE id=?',(user_id,)).fetchone()
        if not target:raise HTTPException(404,'User tidak ditemukan.')
        c.execute('UPDATE users SET password_hash=?,must_change=1,updated_at=? WHERE id=?',(hash_password(temp),now(),user_id))
        c.execute('DELETE FROM sessions WHERE user_id=?',(user_id,))
        audit(c,u['id'],'reset_password','user',user_id)
    return {'temporary_password':temp,'must_change':True}


def clean_payload(kind,data,creating=True):
    allowed=FIELDS[kind]-READ_ONLY_FIELDS.get(kind,set())
    if kind=='referral' and creating: allowed={'referrer_student_id','new_student_name','new_student_id','admission_record_id','attribution_note','notes'}
    if kind=='referral' and not creating:allowed={'new_student_name','new_student_id','admission_record_id','attribution_note','notes'}
    if kind=='scholarship' and not creating:allowed={'start_date','end_date','sk_number','status'}
    if kind=='annual_review':allowed-={'status','final_tier'}
    bad=set(data)-allowed
    if bad:raise HTTPException(400,'Field tidak dapat diubah melalui formulir ini: '+', '.join(sorted(bad)))
    for k,v in data.items():
        if isinstance(v,str) and len(v)>10000:raise HTTPException(400,k+' terlalu panjang.')
    if kind=='scholarship' and creating and int(data.get('tier',0)) not in (50,70,100):raise HTTPException(400,'Kategori beasiswa harus 50, 70, atau 100%.')
    if kind=='annual_review' and creating:
        for key in ('contribution_score','academic_score','character_score'):
            try: v=float(data.get(key,0))
            except (ValueError,TypeError):raise HTTPException(400,'Nilai harus numerik.')
            if v<0 or v>100:raise HTTPException(400,'Nilai harus antara 0 sampai 100.')
        if float(data.get('gpa',0))<0 or float(data.get('gpa',0))>4:
            raise HTTPException(400,'IPK harus 0 sampai 4.')
    if kind=='task' and creating and not data.get('title') or kind=='event' and creating and not data.get('name') or kind=='campaign' and creating and not data.get('name'):
        raise HTTPException(400,'Nama atau judul wajib diisi.')
    return data

def serialize_for(u,kind,r):
    o=dict(r)
    if kind=='student' and u['role'] not in ('admin','wri'):
        for x in ('email','notes','nim'):o.pop(x,None)
    if kind=='referral' and u['role'] not in ('admin','pmb','finance'):
        for x in ('admission_record_id','attribution_note'):o.pop(x,None)
    return o

@app.get('/api/records/{kind}')
def records(kind:str,u=Depends(auth)):
    if kind not in KINDS:raise HTTPException(404,'Modul tidak tersedia.')
    with connect() as c:
        rows=[serialize_for(u,kind,r) for r in list_records(c,kind) if can_read(u,kind,r)]
    return {'items':rows}

@app.post('/api/records/{kind}')
def create_record(kind:str,body:RecordPayload,u=Depends(auth)):
    if kind not in KINDS or kind in ('approval','exemption','weekly_score'):
        raise HTTPException(404,'Modul tidak tersedia.')
    unit=body.unit or ({'event':'WR I','campaign':'WR II','referral':'WR II','student':'WR I','scholarship':'ADMIN','annual_review':'WR I','sop':'ADMIN','taiwan_application':'WR I'}.get(kind,u['unit']))
    if kind=='event' and unit!='WR I' or kind in ('campaign','referral') and unit!='WR II':raise HTTPException(400,'Unit tidak sesuai modul.')
    if not can_create(u,kind,unit):raise HTTPException(403,'Tidak berwenang membuat data pada unit ini.')
    d=clean_payload(kind,body.data,True)
    if kind in ('event','campaign') and u['role']=='operator' and d.get('status') not in (None,'Perencanaan','Rencana'):
        raise HTTPException(403,'Operator hanya boleh membuat rancangan awal.')
    if kind=='task':d.setdefault('status','Ditugaskan')
    if kind=='event':d.setdefault('status','Perencanaan')
    if kind=='campaign':d.setdefault('status','Rencana')
    if kind=='referral':d.update(status='Menunggu Verifikasi',payment_status='Pending')
    if kind=='taiwan_application':
        if not isinstance(d.get('academics_confirmed',False),bool) or not isinstance(d.get('partner_requirements_confirmed',False),bool):
            raise HTTPException(400,'Konfirmasi akademik dan mitra harus true/false.')
        if d.get('partner') not in ('Shih Hsin University','Shih Chien University','NCUE','MCUT'):
            raise HTTPException(400,'Mitra Taiwan tidak dikenal.')
        if d.get('partner')=='MCUT' and d.get('program_type')!='3+2':raise HTTPException(400,'MCUT harus mengikuti skema 3+2.')
        if d.get('partner')!='MCUT' and d.get('program_type')!='Student Exchange':raise HTTPException(400,'Skema selain MCUT harus Student Exchange.')
        if d.get('contribution_path') not in ('Referensi','Kontribusi Strategis','Proyek Khusus'):
            raise HTTPException(400,'Jalur kontribusi tidak valid.')
        d.update(status='Menunggu Evaluasi')
    if kind=='annual_review':
        d.update(status='Menunggu Rektor')
        d['total_score']=round(.60*float(d.get('contribution_score',0))+.25*float(d.get('academic_score',0))+.15*float(d.get('character_score',0)),2)
    prefix={'student':'STD','scholarship':'SCH','event':'EVT','campaign':'CMP','task':'TSK','attendance':'ABS','referral':'REF','exemption':'EXM','annual_review':'REV','approval':'APR','sop':'SOP','weekly_score':'SCO','taiwan_application':'TWN'}[kind]
    try:
        with connect() as c:
            c.execute('BEGIN IMMEDIATE')
            if kind in ('scholarship','task','attendance','referral','annual_review','taiwan_application'):
                student_key='referrer_student_id' if kind=='referral' else 'student_id'
                student_id=d.get(student_key)
                if not student_id or not get_record(c,'student',student_id):
                    raise HTTPException(400,'Mahasiswa pemilik record wajib terdaftar di Data Mahasiswa.')
            if kind=='scholarship':
                year=str(d.get('academic_year','2027/2028'));tier=int(d['tier'])
                cap={100:2,70:3,50:50}[tier]
                total=sum(int(x.get('tier',0))==tier and x.get('academic_year')==year and x.get('status','Aktif')!='Dibatalkan' for x in list_records(c,'scholarship'))
                if total>=cap:raise HTTPException(409,f'Kuota beasiswa {tier}% penuh ({cap} mahasiswa).')
            rid=uid(prefix)
            result=save_record(c,kind,rid,unit,d,u['id'])
            c.execute('COMMIT')
            return {'item':serialize_for(u,kind,result)}
    except HTTPException:raise
    except ValueError as e:raise HTTPException(409,str(e))

@app.patch('/api/records/{kind}/{record_id}')
def update_record(kind:str,record_id:str,body:PatchPayload,u=Depends(auth)):
    if kind not in KINDS or kind in ('approval','exemption','sop','weekly_score'):raise HTTPException(404,'Modul tidak tersedia.')
    with connect() as c:
        c.execute('BEGIN IMMEDIATE')
        item=get_record(c,kind,record_id)
        if not item:raise HTTPException(404,'Data tidak ditemukan.')
        if not can_update(u,kind,item):raise HTTPException(403,'Anda tidak berwenang mengubah data ini.')
        patch=clean_payload(kind,body.data,False)
        if kind=='annual_review' and item.get('status') in ('Disetujui','Ditolak'):
            raise HTTPException(409,'Evaluasi sudah diputuskan Rektor dan terkunci.')
        if kind=='taiwan_application' and ('academics_confirmed' in patch and not isinstance(patch['academics_confirmed'],bool) or 'partner_requirements_confirmed' in patch and not isinstance(patch['partner_requirements_confirmed'],bool)):
            raise HTTPException(400,'Konfirmasi wajib boolean.')
        if kind=='taiwan_application' and item.get('status') in ('Persyaratan Internal Terpenuhi','Ditolak'):
            raise HTTPException(409,'Permohonan Taiwan sudah diputuskan.')
        if kind in ('event','campaign') and u['role']=='operator' and patch.get('status') not in (None,'Perencanaan','Rencana','Diajukan'):
            raise HTTPException(403,'Operator tidak dapat mengesahkan kegiatan/kampanye.')
        if kind=='task' and patch.get('status') in ('Diterima','Selesai'):
            raise HTTPException(400,'Tugas hanya dapat diterima oleh PIC melalui QC.')
        if kind=='referral':
            # PMB cannot impersonate finance; only dedicated verification routes.
            pass
        if kind=='annual_review':
            p={**item,**patch}
            patch['total_score']=round(.60*float(p.get('contribution_score',0))+.25*float(p.get('academic_score',0))+.15*float(p.get('character_score',0)),2)
        try:r=save_record(c,kind,record_id,item['unit'],patch,u['id'],body.version)
        except ValueError:raise HTTPException(409,'Data telah berubah. Segarkan halaman sebelum menyimpan.')
        c.execute('COMMIT')
    return {'item':serialize_for(u,kind,r)}

@app.get('/api/evidence/{task_id}')
def task_files(task_id:str,u=Depends(auth)):
    with connect() as c:
        task=get_record(c,'task',task_id)
        if not task:raise HTTPException(404,'Tugas tidak ditemukan')
        if not can_read(u,'task',task):raise HTTPException(403,'Akses ditolak')
        files=c.execute('SELECT * FROM evidence_files WHERE task_id=? ORDER BY created_at DESC',(task_id,)).fetchall()
        return {'items':[{k:r[k] for k in ('id','task_id','original_name','mime_type','size_bytes','created_at','drive_id')} for r in files]}

@app.post('/api/evidence/{task_id}/upload')
async def upload_file(task_id:str,file:UploadFile=File(...),u=Depends(auth)):
    with connect() as c:
        task=get_record(c,'task',task_id)
        if not task:raise HTTPException(404,'Tugas tidak ditemukan.')
        if not can_update(u,'task',task) and not (u['role']=='reviewer' and is_scope(u,task['unit'])):
            raise HTTPException(403,'Tidak berwenang mengunggah bukti pada tugas ini.')
    original=pathlib.Path(file.filename or '').name[:110]
    ext=pathlib.Path(original).suffix.lower()
    if ext not in {'.pdf','.jpg','.jpeg','.png','.webp','.mp4','.mov','.docx','.xlsx'}:
        raise HTTPException(400,'Format file tidak diperbolehkan.')
    uploaded=data_dir()/'uploads';uploaded.mkdir(exist_ok=True)
    fid=uid('DOC');filename=fid+ext;dest=uploaded/filename
    size=0;h=hashlib.sha256()
    try:
        with dest.open('wb') as stream:
            while chunk:=await file.read(1024*1024):
                size+=len(chunk)
                if size>MAX_UPLOAD_BYTES:raise HTTPException(413,'File melebihi batas ukuran upload.')
                stream.write(chunk);h.update(chunk)
        if size==0:raise HTTPException(400,'File kosong tidak dapat diunggah.')
    except Exception:
        dest.unlink(missing_ok=True)
        raise
    mtype=mimetypes.guess_type(original)[0] or 'application/octet-stream'
    with connect() as c:
        c.execute('INSERT INTO evidence_files VALUES(?,?,?,?,?,?,?,?,?,?)',(fid,task_id,u['id'],original,mtype,size,h.hexdigest(),filename,None,now()))
        audit(c,u['id'],'upload_evidence','task',task_id,details=fid)
        d={'status':'Menunggu QC'}
        save_record(c,'task',task_id,task['unit'],d,u['id'],task['version'])
    return {'ok':True,'file_id':fid,'name':original,'bytes':size}

@app.get('/api/evidence/file/{file_id}')
def download_file(file_id:str,u=Depends(auth)):
    with connect() as c:
        f=c.execute('SELECT * FROM evidence_files WHERE id=?',(file_id,)).fetchone()
        if not f:raise HTTPException(404,'Bukti tidak ditemukan.')
        task=get_record(c,'task',f['task_id'])
        if not task or not can_read(u,'task',task):raise HTTPException(403,'Tidak berwenang membuka bukti ini.')
        p=data_dir()/'uploads'/f['stored_name']
        if not p.is_file():raise HTTPException(404,'File tidak ditemukan pada server.')
        return FileResponse(p,filename=f['original_name'],media_type='application/octet-stream',content_disposition_type='attachment')

@app.post('/api/tasks/{task_id}/review')
def review(task_id:str,body:ReviewPayload,u=Depends(auth)):
    if u['role'] not in ('admin','wri','wrii','wriii','reviewer'):
        raise HTTPException(403,'Hanya reviewer / pimpinan unit yang dapat melakukan QC.')
    if body.decision not in ('Diterima','Perlu Revisi','Ditolak'):
        raise HTTPException(400,'Keputusan QC tidak valid.')
    with connect() as c:
        c.execute('BEGIN IMMEDIATE');task=get_record(c,'task',task_id)
        if not task:raise HTTPException(404,'Tugas tidak ditemukan.')
        if not is_scope(u,task['unit']):raise HTTPException(403,'Bukan tugas unit Anda.')
        if task['version']!=body.version:raise HTTPException(409,'Versi berubah, segarkan data.')
        file_count=c.execute('SELECT count(*) n FROM evidence_files WHERE task_id=?',(task_id,)).fetchone()['n']
        if body.decision=='Diterima' and file_count<1:raise HTTPException(400,'Tidak bisa menerima tugas tanpa bukti yang diunggah.')
        score=round((.40*body.quality+.25*body.target+.15*body.timeliness+.10*body.initiative+.10*body.teamwork)*20,1)
        upd={'status':body.decision,'review_score':score,'review_note':body.note,'reviewed_by':u['id'],'reviewed_at':now()}
        result=save_record(c,'task',task_id,task['unit'],upd,u['id'],body.version)
        weekly={'task_id':task_id,'student_id':task.get('student_id',''),'reviewer_id':u['id'],
          'quality_0_5':body.quality,'target_0_5':body.target,'timeliness_0_5':body.timeliness,
          'initiative_0_5':body.initiative,'teamwork_0_5':body.teamwork,'weighted_score':score,
          'result_status':body.decision,'review_note':body.note,'reviewed_at':now()}
        save_record(c,'weekly_score',uid('SCO'),task['unit'],weekly,u['id'])
        c.execute('COMMIT')
    return {'item':result}

@app.post('/api/referrals/{rid}/verify-pmb')
def verify_pmb(rid:str,body:VerifyPayload,u=Depends(auth)):
    if u['role'] not in ('admin','pmb'):raise HTTPException(403,'Verifikasi PMB hanya untuk PMB/Rektor.')
    with connect() as c:
        c.execute('BEGIN IMMEDIATE');r=get_record(c,'referral',rid)
        if not r:raise HTTPException(404,'Referensi tidak ditemukan.')
        if r['version']!=body.version:raise HTTPException(409,'Versi berubah.')
        if body.verified and not r.get('new_student_id'):
            raise HTTPException(400,'Nomor pendaftaran mahasiswa baru wajib diisi sebelum verifikasi.')
        if body.verified:
            duplicates=[x for x in list_records(c,'referral') if x['id']!=rid and x.get('new_student_id')==r.get('new_student_id') and x.get('pm_verified_at')]
            if duplicates:raise HTTPException(409,'Mahasiswa baru ini sudah diatribusikan kepada pemberi referensi lain.')
        upd={'pm_verified_at':now() if body.verified else '', 'pm_verified_by':u['id'] if body.verified else '',
             'attribution_note':body.reference_note[:300],'status':'PMB Terverifikasi' if body.verified else 'Menunggu Verifikasi'}
        result=save_record(c,'referral',rid,'WR II',upd,u['id'],body.version)
        c.execute('COMMIT')
    return {'item':result}

@app.post('/api/referrals/{rid}/verify-finance')
def verify_finance(rid:str,body:VerifyPayload,u=Depends(auth)):
    if u['role'] not in ('admin','finance'):raise HTTPException(403,'Verifikasi pembayaran hanya untuk Finance/Rektor.')
    with connect() as c:
        c.execute('BEGIN IMMEDIATE');r=get_record(c,'referral',rid)
        if not r:raise HTTPException(404,'Referensi tidak ditemukan.')
        if r['version']!=body.version:raise HTTPException(409,'Versi berubah.')
        if body.verified and not r.get('pm_verified_at'):
            raise HTTPException(400,'Verifikasi PMB harus selesai lebih dahulu.')
        patch={'finance_verified_at':now() if body.verified else '', 'finance_verified_by':u['id'] if body.verified else '',
               'payment_status':'Lunas/Terpenuhi' if body.verified else 'Belum Terpenuhi',
               'status':'Terverifikasi' if body.verified else 'PMB Terverifikasi'}
        result=save_record(c,'referral',rid,'WR II',patch,u['id'],body.version)
        c.execute('COMMIT')
    return {'item':result}

@app.post('/api/referrals/{rid}/saturday-exemption')
def saturday_exemption(rid:str,body:ExemptionPayload,u=Depends(auth)):
    if u['role'] not in ('admin','wrii'):raise HTTPException(403,'Hanya WR II/Rektor yang dapat mengesahkan pembebasan Sabtu.')
    with connect() as c:
        c.execute('BEGIN IMMEDIATE');r=get_record(c,'referral',rid)
        if not r:raise HTTPException(404,'Referensi tidak ditemukan.')
        if r['version']!=body.version:raise HTTPException(409,'Versi berubah.')
        if body.approve and (not r.get('pm_verified_at') or not r.get('finance_verified_at')):
            raise HTTPException(400,'Pembebasan belum dapat disetujui: PMB dan Keuangan belum memverifikasi.')
        if body.approve:
            exists=[x for x in list_records(c,'exemption') if x.get('referral_id')==rid and x.get('status')=='Disetujui']
            if exists:raise HTTPException(409,'Referensi ini sudah memiliki pembebasan Sabtu.')
            today=datetime.datetime.now(ZoneInfo('Asia/Jakarta')).date();until=today.replace(year=today.year+1) if not(today.month==2 and today.day==29) else datetime.date(today.year+1,2,28)
            ex={'student_id':r['referrer_student_id'],'referral_id':rid,'exemption_type':'Pembebasan Sabtu',
                'start_date':today.isoformat(),'end_date':(until-datetime.timedelta(days=1)).isoformat(),
                'status':'Disetujui','approved_by':u['id'],'approved_at':now(),'notes':body.note[:500]}
            exr=save_record(c,'exemption',uid('EXM'),'WR II',ex,u['id'])
            used=str(r.get('used_for',''))
            patch={'used_for': (used+'; ' if used else '')+'Sabtu'}
            save_record(c,'referral',rid,'WR II',patch,u['id'],body.version)
        else:
            exr=None
        c.execute('COMMIT')
    return {'ok':True,'exemption':exr}

@app.post('/api/taiwan/{rid}/decision')
def taiwan_decision(rid:str,body:TaiwanDecisionPayload,u=Depends(auth)):
    require_admin(u)
    with connect() as c:
        c.execute('BEGIN IMMEDIATE')
        r=get_record(c,'taiwan_application',rid)
        if not r:raise HTTPException(404,'Pengajuan Taiwan tidak ditemukan.')
        if r['version']!=body.version:raise HTTPException(409,'Data telah berubah.')
        if r.get('status') in ('Persyaratan Internal Terpenuhi','Ditolak'):
            raise HTTPException(409,'Keputusan sudah ditetapkan.')
        if body.approve:
            if not r.get('academics_confirmed') or not r.get('partner_requirements_confirmed'):
                raise HTTPException(400,'Persyaratan akademik dan mitra belum dikonfirmasi.')
            if r.get('contribution_path')=='Referensi':
                ref=get_record(c,'referral',r.get('referral_id',''))
                if not ref or ref.get('referrer_student_id')!=r['student_id'] or ref.get('status')!='Terverifikasi':
                    raise HTTPException(400,'Referensi belum sah atau bukan milik mahasiswa tersebut.')
                previously=str(ref.get('used_for') or '')
                if previously and not body.allow_dual_use:
                    raise HTTPException(409,'Referensi sudah digunakan untuk fasilitas lain. Setujui penggunaan ganda secara eksplisit.')
                save_record(c,'referral',ref['id'],ref['unit'],
                    {'used_for':(previously+'; ' if previously else '')+'Taiwan '+rid},u['id'],ref['version'])
            else:
                task=get_record(c,'task',r.get('alternative_task_id',''))
                if not task or task.get('student_id')!=r['student_id'] or task.get('status')!='Diterima' or float(task.get('review_score',0))<85:
                    raise HTTPException(400,'Jalur alternatif wajib mempunyai tugas selesai dengan QC minimal 85/100.')
        patch={'status':'Persyaratan Internal Terpenuhi' if body.approve else 'Ditolak',
               'approved_by':u['id'],'approved_at':now(),'approved_dual_use':body.allow_dual_use,
               'notes':str(r.get('notes',''))+' | Keputusan Rektor: '+body.note[:500]}
        out=save_record(c,'taiwan_application',rid,r['unit'],patch,u['id'],body.version)
        c.execute('COMMIT')
    return {'item':out,'warning':'Pemenuhan syarat internal BUKAN jaminan penerimaan universitas Taiwan ataupun visa.'}

@app.post('/api/annual-reviews/{rid}/decision')
def annual_decision(rid:str,body:AnnualDecisionPayload,u=Depends(auth)):
    require_admin(u)
    with connect() as c:
        c.execute('BEGIN IMMEDIATE');r=get_record(c,'annual_review',rid)
        if not r:raise HTTPException(404,'Evaluasi tidak ditemukan.')
        if r['version']!=body.version:raise HTTPException(409,'Versi berubah.')
        if body.approve:
            tier=body.final_tier if body.final_tier is not None else r.get('recommended_tier')
            if tier not in (0,50,70,100):raise HTTPException(400,'Kategori final tidak sah.')
            minimum={100:(3.6,90),70:(3.25,80),50:(3.0,70),0:(0,0)}[tier]
            if float(r.get('gpa',0))<minimum[0] or float(r.get('total_score',0))<minimum[1]:
                raise HTTPException(400,'IPK atau skor evaluasi belum memenuhi syarat kategori ini.')
            final=tier
        else:final=0
        upd={'status':'Disetujui' if body.approve else 'Ditolak','final_tier':final,
             'decision_note':body.note,'rector_approved_at':now()}
        x=save_record(c,'annual_review',rid,'WR I',upd,u['id'],body.version)
        c.execute('COMMIT')
    return {'item':x}

@app.get('/api/dashboard')
def dashboard(u=Depends(auth)):
    with connect() as c:
        records={k:[r for r in list_records(c,k) if can_read(u,k,r)] for k in ('student','scholarship','event','campaign','task','attendance','referral','exemption','annual_review','sop','weekly_score','taiwan_application')}
        files={}
        for task in records['task']:
            files[task['id']]=c.execute('SELECT count(*) n FROM evidence_files WHERE task_id=?',(task['id'],)).fetchone()['n']
        if u['role']=='admin':
            approvals=c.execute("SELECT count(*) n FROM records WHERE kind='annual_review' AND json_extract(data_json,'$.status')='Menunggu Rektor'").fetchone()['n']
        else:approvals=0
        overdue=sum(bool(t.get('due_date') and t['due_date']<datetime.date.today().isoformat() and t.get('status') not in ('Diterima','Ditolak','Dibatalkan')) for t in records['task'])
        calendar_month=datetime.datetime.now(ZoneInfo('Asia/Jakarta')).date().strftime('%Y-%m')
        calendar_month_events=[e for e in records['event'] if str(e.get('date','')).startswith(calendar_month)]
        calendar_month_campaigns=[e for e in records['campaign'] if str(e.get('month','')).startswith(calendar_month)]
        academic_active=datetime.date(2027,9,1)<=datetime.datetime.now(ZoneInfo('Asia/Jakarta')).date()<datetime.date(2028,7,1)
        return {'user':safe_user(u),'counts':{k:len(v) for k,v in records.items()},
                'calendar_month':calendar_month,'academic_active':academic_active,
                'monthly':{'wri_events':len(calendar_month_events),'wrii_campaigns':len(calendar_month_campaigns)},
                'monthly_alerts':([x for x in [
                   'WR I belum mempunyai kegiatan bulan ini' if not calendar_month_events else None,
                   'WR II belum mempunyai kampanye bulan ini' if not calendar_month_campaigns else None] if x] if academic_active else []),
                'pending_qc':sum(t.get('status')=='Menunggu QC' for t in records['task']),
                'accepted_tasks':sum(t.get('status')=='Diterima' for t in records['task']),
                'overdue_tasks':overdue,'pending_annual':approvals,
                'evidence_counts':files,'recent_tasks':records['task'][:8],
                'recent_events':records['event'][:5],'recent_campaigns':records['campaign'][:5],
                'recent_referrals':records['referral'][:5],
                'sop_count':len(records['sop'])}

@app.get('/api/audit')
def get_audit(u=Depends(auth)):
    require_admin(u)
    with connect() as c:
        rows=c.execute('SELECT id,at,actor_id,actor_role,action,kind,record_id,details FROM audit ORDER BY at DESC,id DESC LIMIT 250').fetchall()
    return {'items':[dict(r) for r in rows]}

@app.get('/api/integrations/status')
def integration_status(u=Depends(auth)):
    require_admin(u)
    with connect() as c:pending=c.execute("SELECT count(*) n FROM sync_queue WHERE status='pending'").fetchone()['n']
    return {'google':google_sync.config(),'pending_sync':pending,'storage':'SQLite (authoritative) + optional Sheets mirror / Drive backup'}

@app.post('/api/integrations/sync')
def integration_sync(u=Depends(auth)):
    require_admin(u)
    return google_sync.sync_queue(max_items=40)

@app.post('/api/integrations/upload-backups')
def google_backup_evidence(u=Depends(auth)):
    require_admin(u)
    if not google_sync.config()['configured']:raise HTTPException(409,'Hubungan Google belum diatur di server.')
    count=0;errors=[]
    with connect() as c:
        rows=c.execute('SELECT * FROM evidence_files WHERE drive_id IS NULL ORDER BY created_at LIMIT 15').fetchall()
        for f in rows:
            try:
                drive_id=google_sync.upload_to_drive(data_dir()/'uploads'/f['stored_name'],f['original_name'],f['mime_type'])
                c.execute('UPDATE evidence_files SET drive_id=? WHERE id=?',(drive_id,f['id']))
                count+=1
            except Exception as e:errors.append(str(e)[:160])
    return {'backed_up':count,'errors':errors}

# Static SOP files are only accessible to authenticated staff, unlike public JS/CSS.
@app.get('/api/manual/{filename}')
def download_manual(filename:str,u=Depends(auth)):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+',filename):raise HTTPException(400,'Nama file tidak sah.')
    p=BASE/'docs'/filename
    if not p.is_file():raise HTTPException(404,'Dokumen tidak tersedia.')
    return FileResponse(p,filename=filename,media_type='application/octet-stream')
