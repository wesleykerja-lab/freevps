"""Optional Google Sheets mirror + Google Drive evidence backup.
SQLite is authoritative; Google integration is explicit and fails closed without credentials.
Never store Google credentials in the ZIP, browser, or Google Sheets.
"""
from __future__ import annotations
import os,json,time,base64,requests,datetime,pathlib,mimetypes
from urllib.parse import quote
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import padding
from .database import connect,now,get_record

SHEET_MAP={'student':'STUDENTS','scholarship':'SCHOLARSHIPS','event':'EVENTS_WRI',
 'campaign':'CAMPAIGNS_WRII','task':'TASKS','attendance':'ATTENDANCE',
 'referral':'REFERRALS_RESTRICTED','exemption':'EXEMPTIONS','annual_review':'ANNUAL_REVIEWS',
 'approval':'APPROVALS','sop':'SOP_LIBRARY','audit':'AUDIT_LOG','weekly_score':'WEEKLY_SCORES','taiwan_application':'TAIWAN_APPLICATIONS'}
GOOGLE_SCOPES='https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive.file'
TOKEN={}

def config():
    path=os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON_PATH','')
    p=pathlib.Path(path) if path else None
    return {'configured':bool(p and p.is_file() and os.getenv('GOOGLE_SHEET_ID') and os.getenv('GOOGLE_DRIVE_FOLDER_ID')),
            'sheet_id':os.getenv('GOOGLE_SHEET_ID',''),
            'folder_id':os.getenv('GOOGLE_DRIVE_FOLDER_ID','')}

def _b64(x):return base64.urlsafe_b64encode(x).rstrip(b'=').decode()

def token():
    if not config()['configured']:raise RuntimeError('Google belum dikonfigurasi. Lengkapi service account dan izin editor Drive.')
    if TOKEN.get('expires',0)>time.time()+120:return TOKEN['access']
    sa=json.loads(pathlib.Path(os.environ['GOOGLE_SERVICE_ACCOUNT_JSON_PATH']).read_text())
    header=_b64(json.dumps({'alg':'RS256','typ':'JWT'}).encode())
    issued=int(time.time())
    payload=_b64(json.dumps({'iss':sa['client_email'],'scope':GOOGLE_SCOPES,'aud':'https://oauth2.googleapis.com/token','iat':issued,'exp':issued+3500}).encode())
    msg=(header+'.'+payload).encode()
    private_key=serialization.load_pem_private_key(sa['private_key'].encode(),password=None)
    sign=private_key.sign(msg,padding.PKCS1v15(),hashes.SHA256())
    assertion=header+'.'+payload+'.'+_b64(sign)
    res=requests.post('https://oauth2.googleapis.com/token',data={'grant_type':'urn:ietf:params:oauth:grant-type:jwt-bearer','assertion':assertion},timeout=15)
    res.raise_for_status();body=res.json()
    TOKEN.update(access=body['access_token'],expires=time.time()+int(body.get('expires_in',3600)))
    return TOKEN['access']

def request(method,url,**kwargs):
    headers=kwargs.pop('headers',{})
    headers['Authorization']='Bearer '+token()
    res=requests.request(method,url,headers=headers,timeout=25,**kwargs)
    if not res.ok: raise RuntimeError(f'Google API HTTP {res.status_code}: {res.text[:350]}')
    return res.json() if res.content else {}

def fields_of(c,kind,rid):
    if kind=='audit':
        r=c.execute('SELECT * FROM audit WHERE id=?',(rid,)).fetchone()
        if not r:return None
        return {'event_id':r['id'],'timestamp':r['at'],'actor_user_id':r['actor_id'],'role':r['actor_role'],'action':r['action'],
                'record_type':r['kind'],'record_id':r['record_id'],'old_snapshot_hash':r['before_hash'],'new_snapshot_hash':r['after_hash'],
                'reason':r['details'],'request_id':''}
    o=get_record(c,kind,rid)
    if not o:return None
    # Map frontend record names to established Google Sheets headers; no credentials/passwords synced.
    translations={'student':{'student_id':'id','nama':'name','prodi':'program','angkatan':'cohort','email':'email','status_aktif':'status'},
                  'scholarship':{'award_id':'id','student_id':'student_id','tahun_akademik':'academic_year','kategori_persen':'tier',
                                 'tanggal_mulai':'start_date','tanggal_akhir':'end_date','nomor_sk':'sk_number'},
                  'event':{'event_id':'id','nama_event':'name','kategori':'category','tujuan':'objective',
                           'tanggal_mulai':'date','tanggal_selesai':'end_date','proposal_drive_id':'proposal_file_id',
                           'status':'status','pic':'pic','target_peserta':'target_attendees','peserta_aktual':'attendees',
                           'aar_drive_id':'report_file_id'},
                  'campaign':{'campaign_id':'id','nama_campaign':'name','bulan':'month','pesan_utama':'message','target_output':'target',
                              'status':'status','pic':'pic'},
                  'task':{'task_id':'id','owner_unit':'unit','student_id':'student_id','jenis_tugas':'category','brief':'brief',
                          'target_output':'target','tanggal_tugas':'date','due_at':'due_date','status':'status',
                          'pic_id':'pic','created_by':'created_by'},
                  'attendance':{'attendance_id':'id','student_id':'student_id','tanggal':'date','task_id':'task_id',
                                'owner_unit':'unit','status':'status','alasan':'reason','approval_id':'approval_id'},
                  'referral':{'referral_id':'id','referrer_student_id':'referrer_student_id','new_student_id':'new_student_id',
                              'status':'status','payment_status':'payment_status','pm_verified_at':'pm_verified_at',
                              'finance_verified_at':'finance_verified_at'},
                  'exemption':{'exemption_id':'id','student_id':'student_id','referral_id':'referral_id',
                               'exemption_type':'exemption_type','start_date':'start_date','end_date':'end_date','approval_status':'status'},
                  'annual_review':{'review_id':'id','student_id':'student_id','tahun_akademik':'academic_year','contribution_score':'contribution_score',
                                   'academic_score':'academic_score','character_score':'character_score','total_score':'total_score',
                                   'ipk':'gpa','requested_tier':'requested_tier','recommended_tier':'recommended_tier','final_tier':'final_tier'},
                  'approval':{'approval_id':'id','record_type':'record_type','record_id':'record_id','decision':'decision'},
                  'sop':{'sop_id':'id','title':'title','version':'sop_version','drive_file_id':'file_id','status':'status'},
                  'weekly_score':{'score_id':'id','task_id':'task_id','student_id':'student_id','reviewer_id':'reviewer_id','quality_0_5':'quality_0_5','target_0_5':'target_0_5',
                      'timeliness_0_5':'timeliness_0_5','initiative_0_5':'initiative_0_5','teamwork_0_5':'teamwork_0_5','weighted_score':'weighted_score','result_status':'result_status',
                      'review_note':'review_note','reviewed_at':'reviewed_at'},
                  'taiwan_application':{'application_id':'id','student_id':'student_id','partner':'partner','program_type':'program_type','contribution_path':'contribution_path','referral_id':'referral_id',
                      'alternative_task_id':'alternative_task_id','gpa':'gpa','status':'status','approved_by':'approved_by','approved_at':'approved_at'}}
    d=dict(o)
    for target,source in translations.get(kind,{}).items(): d[target]=o.get(source,'')
    d['row_version']=o.get('version',1)
    return d

def sync_one(c,kind,rid):
    sheet=SHEET_MAP.get(kind)
    if not sheet:return 'skipped'
    data=fields_of(c,kind,rid)
    if not data:return 'not_found'
    sid=config()['sheet_id'];base=f'https://sheets.googleapis.com/v4/spreadsheets/{quote(sid)}'
    header=request('GET',base+'/values/'+quote(f"'{sheet}'!1:1",safe=''),params={'valueRenderOption':'FORMATTED_VALUE'}).get('values',[[]])[0]
    if not header:raise RuntimeError('Google tab '+sheet+' tidak mempunyai header')
    identifier=str(data.get(header[0],rid))
    col_a=request('GET',base+'/values/'+quote(f"'{sheet}'!A2:A",safe='')).get('values',[])
    row_idx=next((i+2 for i,v in enumerate(col_a) if v and str(v[0])==identifier),None)
    values=[str(data.get(h,'')) if data.get(h,'') is not None else '' for h in header]
    if row_idx is not None:
        request('PUT',base+'/values/'+quote(f"'{sheet}'!A{row_idx}",safe=''),
                params={'valueInputOption':'RAW'},json={'values':[values]})
    else:
        request('POST',base+'/values/'+quote(f"'{sheet}'!A1:Z",safe='')+':append',
                params={'valueInputOption':'RAW','insertDataOption':'INSERT_ROWS'},json={'values':[values]})
    return 'synced'

def sync_queue(max_items=40):
    if not config()['configured']:return {'configured':False,'synced':0,'failed':0,'pending':None}
    count=0;failed=0
    with connect() as c:
        entries=c.execute("SELECT * FROM sync_queue WHERE status='pending' ORDER BY queued_at,id LIMIT ?",(min(max_items,200),)).fetchall()
        for entry in entries:
            try:
                sync_one(c,entry['kind'],entry['record_id'])
                c.execute("UPDATE sync_queue SET status='synced',synced_at=?,last_error=NULL WHERE id=?",(now(),entry['id']))
                count+=1
            except Exception as e:
                c.execute("UPDATE sync_queue SET tries=tries+1,last_error=? WHERE id=?",(str(e)[:300],entry['id']))
                failed+=1
        pending=c.execute("SELECT count(*) x FROM sync_queue WHERE status='pending'").fetchone()['x']
    return {'configured':True,'synced':count,'failed':failed,'pending':pending}

def upload_to_drive(path,original_name,mime_type):
    """Optional Google Drive backup. Server must have drive.file permission on destination folder."""
    if not config()['configured']:return None
    import uuid
    meta={'name':str(uuid.uuid4())+'_'+original_name[:70], 'parents':[config()['folder_id']]}
    # Google multipart upload; raw content belongs server-side only.
    boundary='cscms'+uuid.uuid4().hex
    prefix=(f'--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n'+json.dumps(meta)+
            f'\r\n--{boundary}\r\nContent-Type: {mime_type}\r\n\r\n').encode()
    suffix=(f'\r\n--{boundary}--\r\n').encode()
    content=prefix+pathlib.Path(path).read_bytes()+suffix
    response=request('POST','https://www.googleapis.com/upload/drive/v3/files',params={'uploadType':'multipart','fields':'id,name'},
                     headers={'Content-Type':f'multipart/related; boundary={boundary}'},data=content)
    return response.get('id')
