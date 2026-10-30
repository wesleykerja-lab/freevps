"""Hash-only password storage and rotating, server-stored login sessions."""
from __future__ import annotations
import os,secrets,hashlib,datetime
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError,VerificationError
from fastapi import HTTPException,Request
from .database import now,uid

hasher=PasswordHasher(time_cost=3,memory_cost=65536,parallelism=2)
ALLOWED_ROLES={'admin','wri','wrii','wriii','operator','reviewer','pmb','finance'}
AUTH_ROLES={'admin','wri','wrii','wriii','operator','reviewer','pmb','finance'}
DEFAULT_TTL_HRS=10

def hash_password(password): return hasher.hash(password)
def verify_password(password,digest):
    try: return hasher.verify(digest,password)
    except (VerifyMismatchError,VerificationError,ValueError): return False

def password_ok(p):
    if not isinstance(p,str) or len(p)<12 or len(p)>128:return False
    return sum([any(x.islower() for x in p),any(x.isupper() for x in p),any(x.isdigit() for x in p),any(not x.isalnum() for x in p)])>=3

def safe_user(row):
    return {k:row[k] for k in ('id','username','display_name','email','role','unit','must_change','active','created_at','updated_at') if k in row.keys()}

def session_hash(token):return hashlib.sha256(token.encode('utf8')).hexdigest()

def create_session(c,user):
    token=secrets.token_urlsafe(48)
    csrf=secrets.token_urlsafe(32)
    created=now()
    expiry=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=DEFAULT_TTL_HRS)).isoformat(timespec='seconds')
    c.execute('INSERT INTO sessions VALUES(?,?,?,?,?)',(session_hash(token),user['id'],csrf,expiry,created))
    return token,csrf

def read_session(c,token):
    if not token:return None
    row=c.execute('''SELECT s.csrf_token,s.expires_at,u.* FROM sessions s
                       JOIN users u ON u.id=s.user_id WHERE s.token_hash=?''',(session_hash(token),)).fetchone()
    if not row or not row['active'] or row['expires_at']<now():return None
    return row

def require_admin(u):
    if u['role']!='admin':raise HTTPException(403,'Hanya Rektor/Admin yang berwenang.')

def is_scope(u,unit):
    if u['role']=='admin':return True
    if u['role']=='wri':return unit=='WR I'
    if u['role']=='wrii':return unit=='WR II'
    if u['role']=='wriii':return unit=='WR III'
    if u['role'] in ('operator','reviewer'):
        return bool(u['unit']) and (u['unit']==unit)
    return False

def can_read(u,kind,rec=None):
    role=u['role']; unit=(rec or {}).get('unit','')
    if role=='admin':return True
    if kind in ('student','scholarship','sop'):return role not in ('finance',) or kind=='sop'
    if kind in ('event','campaign','task','attendance','evidence','weekly_score'):
        return is_scope(u,unit)
    if kind=='referral':return role in ('wrii','pmb','finance')
    if kind=='exemption':return role in ('wrii','pmb','finance')
    if kind=='annual_review':return role in ('wri','wrii')
    if kind=='taiwan_application':return role in ('wri','wrii')
    if kind=='approval':return role in ('wri','wrii','wriii') and (not rec or is_scope(u,unit))
    return False

def can_create(u,kind,unit):
    role=u['role']
    if role=='admin':return True
    if kind in ('event','campaign'):
        return (kind=='event' and role in ('wri','operator') and unit=='WR I' and (role!='operator' or u['unit']=='WR I')) or (kind=='campaign' and role in ('wrii','operator') and unit=='WR II' and (role!='operator' or u['unit']=='WR II'))
    if kind=='task':return is_scope(u,unit) and role in ('wri','wrii','wriii','operator')
    if kind=='attendance':return is_scope(u,unit) and role in ('wri','wrii','wriii','operator')
    if kind=='student':return role=='wri'
    if kind=='referral':return role in ('wrii','pmb')
    if kind=='annual_review':return role=='wri'
    if kind=='taiwan_application':return role in ('wri','wrii')
    return False

def can_update(u,kind,rec):
    role=u['role'];unit=rec.get('unit','')
    if role=='admin':return True
    if kind=='event':return role in ('wri','operator') and unit=='WR I' and (role!='operator' or u['unit']=='WR I')
    if kind=='campaign':return role in ('wrii','operator') and unit=='WR II' and (role!='operator' or u['unit']=='WR II')
    if kind in ('task','attendance'):return role in ('wri','wrii','wriii','operator') and is_scope(u,unit)
    if kind=='student':return role=='wri'
    if kind=='referral':return role in ('wrii','pmb')
    if kind=='annual_review':return role=='wri'
    if kind=='taiwan_application':return role in ('wri','wrii') and rec.get('status') not in ('Persyaratan Internal Terpenuhi','Ditolak')
    return False
