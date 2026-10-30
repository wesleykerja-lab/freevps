"""E2E API tests: security, scope, QC, referrals and annual review.
Run: pytest -q
"""
import os,sys,tempfile,pathlib,subprocess
import pytest
from fastapi.testclient import TestClient
from backend.database import init_db,connect,now,uid
from backend.security import hash_password
from backend.main import app

@pytest.fixture
def client(monkeypatch,tmp_path):
    monkeypatch.setenv('CSC_DATA_DIR',str(tmp_path))
    monkeypatch.setenv('CSC_ENV','development')
    init_db()
    with connect() as c:
        c.execute('INSERT INTO users VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
         ('USR-ADMIN','DrSteven','Dr. Steven','', 'admin','ALL',hash_password('StrongBootstrap1!'),1,1,0,None,now(),now()))
    with TestClient(app) as tc:yield tc

def login(c,username,pw):
    r=c.post('/api/auth/login',json={'username':username,'password':pw})
    assert r.status_code==200,r.text
    return r.json()['csrf']
def csrf_headers(csrf):return {'X-CSRF-Token':csrf}

def test_auth_force_change_roles_and_scope(client):
    c=client
    assert c.get('/api/me').status_code==401
    token=login(c,'DrSteven','StrongBootstrap1!')
    assert c.get('/api/records/student').status_code==403
    assert c.post('/api/auth/change-password',json={'old_password':'StrongBootstrap1!','new_password':'short'},headers=csrf_headers(token)).status_code==400
    r=c.post('/api/auth/change-password',json={'old_password':'StrongBootstrap1!','new_password':'CorrectHorseBattery1!'},headers=csrf_headers(token));assert r.status_code==200,r.text
    assert c.get('/api/me').status_code==401
    token=login(c,'DrSteven','CorrectHorseBattery1!')
    r=c.post('/api/users',json={'username':'WR1','display_name':'WR I','role':'wri','unit':'WR I'},headers=csrf_headers(token));assert r.status_code==200,r.text
    temp=r.json()['temporary_password']; assert len(temp)>12
    # create events by admin
    r=c.post('/api/records/event',json={'unit':'WR I','data':{'name':'Seminar Leadership','date':'2027-09-07','pic':'WR I'}},headers=csrf_headers(token));assert r.status_code==200,r.text
    event_id=r.json()['item']['id']
    # login as WR I (same client cookie session rotates): cannot create WR II campaign
    csrf2=login(c,'WR1',temp)
    assert c.get('/api/records/event').status_code==403
    r=c.post('/api/auth/change-password',json={'old_password':temp,'new_password':'WRI-secretPassword123!'},headers=csrf_headers(csrf2));assert r.status_code==200,r.text
    csrf2=login(c,'WR1','WRI-secretPassword123!')
    assert c.get('/api/records/event').status_code==200
    assert c.get('/api/records/campaign').json()['items']==[]
    assert c.post('/api/records/campaign',json={'unit':'WR II','data':{'name':'Promo'}},headers=csrf_headers(csrf2)).status_code==403
    assert c.post('/api/records/event',json={'unit':'WR I','data':{'name':'Imlek','date':'2027-02-08'}},headers=csrf_headers(csrf2)).status_code==200
    assert c.post('/api/records/event',json={'unit':'WR I','data':{'name':'No CSRF'}},headers={}).status_code==403
    with connect() as db:
        assert db.execute("SELECT count(*) n FROM audit").fetchone()['n']>=5


def test_workflow_qc_referral_exemption(client):
    c=client;cs=login(c,'DrSteven','StrongBootstrap1!')
    c.post('/api/auth/change-password',json={'old_password':'StrongBootstrap1!','new_password':'CorrectHorseBattery1!'},headers=csrf_headers(cs))
    cs=login(c,'DrSteven','CorrectHorseBattery1!')
    student=c.post('/api/records/student',json={'unit':'WR I','data':{'name':'Mahasiswa A','program':'TI','cohort':'2027'}},headers=csrf_headers(cs)).json()['item']
    task=c.post('/api/records/task',json={'unit':'WR II','data':{'title':'Video Campus Tour','student_id':student['id'],'target':'1 video 60 detik','pic':'Operator','due_date':'2027-10-01'}},headers=csrf_headers(cs)).json()['item']
    no_evidence=c.post(f'/api/tasks/{task["id"]}/review',json={'version':task['version'],'quality':4,'target':4,'timeliness':4,'initiative':4,'teamwork':4,'decision':'Diterima','note':'baik'},headers=csrf_headers(cs))
    assert no_evidence.status_code==400
    uploaded=c.post(f'/api/evidence/{task["id"]}/upload',files={'file':('hasil.txt',b'not allowed','text/plain')},headers=csrf_headers(cs));assert uploaded.status_code==400,uploaded.text
    uploaded=c.post(f'/api/evidence/{task["id"]}/upload',files={'file':('hasil.pdf',b'%PDF-1.4\nTest document','application/pdf')},headers=csrf_headers(cs));assert uploaded.status_code==200,uploaded.text
    items=c.get(f'/api/evidence/{task["id"]}').json()['items'];assert len(items)==1
    download=c.get('/api/evidence/file/'+items[0]['id']);assert download.status_code==200
    task2=[x for x in c.get('/api/records/task').json()['items'] if x['id']==task['id']][0]
    rr=c.post(f'/api/tasks/{task["id"]}/review',json={'version':task2['version'],'quality':5,'target':4,'timeliness':5,'initiative':5,'teamwork':4,'decision':'Diterima','note':'Sesuai brief'},headers=csrf_headers(cs))
    assert rr.status_code==200,rr.text
    assert rr.json()['item']['review_score']>80
    # referral must require PMB and finance
    ref=c.post('/api/records/referral',json={'unit':'WR II','data':{'referrer_student_id':student['id'],'new_student_name':'Mahasiswa B','new_student_id':'PMB-2027-0101'}},headers=csrf_headers(cs)).json()['item']
    x=c.post(f'/api/referrals/{ref["id"]}/saturday-exemption',json={'version':ref['version'],'approve':True},headers=csrf_headers(cs));assert x.status_code==400
    x=c.post(f'/api/referrals/{ref["id"]}/verify-pmb',json={'version':ref['version'],'verified':True},headers=csrf_headers(cs));assert x.status_code==200,x.text
    ref=x.json()['item']
    x=c.post(f'/api/referrals/{ref["id"]}/verify-finance',json={'version':ref['version'],'verified':True},headers=csrf_headers(cs));assert x.status_code==200,x.text
    ref=x.json()['item']
    x=c.post(f'/api/referrals/{ref["id"]}/saturday-exemption',json={'version':ref['version'],'approve':True,'note':'Verifikasi lengkap'},headers=csrf_headers(cs));assert x.status_code==200,x.text
    assert len(c.get('/api/records/exemption').json()['items'])==1
    y=c.get('/api/records/referral').json()['items'][0]
    assert c.post(f'/api/referrals/{ref["id"]}/saturday-exemption',json={'version':y['version'],'approve':True},headers=csrf_headers(cs)).status_code==409
    assert c.get('/api/dashboard').json()['accepted_tasks']==1


def test_scholarship_review_quota_user_security(client):
    c=client;cs=login(c,'DrSteven','StrongBootstrap1!')
    c.post('/api/auth/change-password',json={'old_password':'StrongBootstrap1!','new_password':'CorrectHorseBattery1!'},headers=csrf_headers(cs))
    cs=login(c,'DrSteven','CorrectHorseBattery1!')
    reviewed_student=c.post('/api/records/student',json={'unit':'WR I','data':{'name':'Mahasiswa Untuk Evaluasi'}},headers=csrf_headers(cs)).json()['item']['id']
    # no ability to set approved fields on create
    r=c.post('/api/records/annual_review',json={'unit':'WR I','data':{'student_id':reviewed_student,'academic_year':'2027/2028','gpa':3.65,'contribution_score':90,'academic_score':95,'character_score':95,'recommended_tier':100,'final_tier':100}},headers=csrf_headers(cs));assert r.status_code==400,r.text
    r=c.post('/api/records/annual_review',json={'unit':'WR I','data':{'student_id':reviewed_student,'academic_year':'2027/2028','gpa':3.65,'contribution_score':90,'academic_score':95,'character_score':95,'recommended_tier':100}},headers=csrf_headers(cs));assert r.status_code==200,r.text
    o=r.json()['item'];assert o['total_score']>=90
    x=c.post(f'/api/annual-reviews/{o["id"]}/decision',json={'version':o['version'],'approve':True,'final_tier':100},headers=csrf_headers(cs));assert x.status_code==200,x.text
    assert x.json()['item']['status']=='Disetujui'
    assert c.get('/api/integrations/status').json()['google']['configured']==False
    assert c.post('/api/integrations/sync',headers=csrf_headers(cs)).json()['configured']==False
    assert c.get('/api/manual/SOP-WR-I-WR-II-DISAHKAN.docx').status_code==200
    assert c.get('/api/manual/../../.env').status_code in (400,404)

def test_taiwan_application_double_use_and_alternative(client):
    c=client;cs=login(c,'DrSteven','StrongBootstrap1!')
    c.post('/api/auth/change-password',json={'old_password':'StrongBootstrap1!','new_password':'CorrectHorseBattery1!'},headers=csrf_headers(cs))
    cs=login(c,'DrSteven','CorrectHorseBattery1!')
    who=c.post('/api/records/student',json={'unit':'WR I','data':{'name':'Mahasiswa Exchange','program':'Sistem Informasi'}},headers=csrf_headers(cs)).json()['item']['id']
    ref=c.post('/api/records/referral',json={'unit':'WR II','data':{'referrer_student_id':who,'new_student_name':'Calon B','new_student_id':'PMB-2027-03'}},headers=csrf_headers(cs)).json()['item']
    ref=c.post(f'/api/referrals/{ref["id"]}/verify-pmb',json={'version':ref['version'],'verified':True},headers=csrf_headers(cs)).json()['item']
    ref=c.post(f'/api/referrals/{ref["id"]}/verify-finance',json={'version':ref['version'],'verified':True},headers=csrf_headers(cs)).json()['item']
    c.post(f'/api/referrals/{ref["id"]}/saturday-exemption',json={'version':ref['version'],'approve':True},headers=csrf_headers(cs))
    req=c.post('/api/records/taiwan_application',json={'unit':'WR I','data':{'student_id':who,'partner':'Shih Hsin University','program_type':'Student Exchange','contribution_path':'Referensi','referral_id':ref['id'],'academics_confirmed':True,'partner_requirements_confirmed':True}},headers=csrf_headers(cs))
    assert req.status_code==200,req.text
    req=req.json()['item']
    no=c.post(f'/api/taiwan/{req["id"]}/decision',json={'version':req['version'],'approve':True,'allow_dual_use':False},headers=csrf_headers(cs))
    assert no.status_code==409,no.text
    yes=c.post(f'/api/taiwan/{req["id"]}/decision',json={'version':req['version'],'approve':True,'allow_dual_use':True,'note':'Pengecualian disetujui'},headers=csrf_headers(cs))
    assert yes.status_code==200,yes.text
    assert yes.json()['item']['status']=='Persyaratan Internal Terpenuhi'
    # Alternative project must be ACCEPTED and score >=85.
    task=c.post('/api/records/task',json={'unit':'WR II','data':{'student_id':who,'title':'Buat Web Beasiswa','pic':'WR II','due_date':'2027-09-01'}},headers=csrf_headers(cs)).json()['item']
    alt=c.post('/api/records/taiwan_application',json={'unit':'WR I','data':{'student_id':who,'partner':'MCUT','program_type':'3+2','contribution_path':'Proyek Khusus','alternative_task_id':task['id'],'academics_confirmed':True,'partner_requirements_confirmed':True}},headers=csrf_headers(cs)).json()['item']
    fail=c.post(f'/api/taiwan/{alt["id"]}/decision',json={'version':alt['version'],'approve':True},headers=csrf_headers(cs));assert fail.status_code==400
    c.post(f'/api/evidence/{task["id"]}/upload',files={'file':('project.pdf',b'%PDF-1.4\nproof','application/pdf')},headers=csrf_headers(cs))
    task=c.get('/api/records/task').json()['items'][0]
    review=c.post(f'/api/tasks/{task["id"]}/review',json={'version':task['version'],'quality':5,'target':5,'timeliness':4,'initiative':5,'teamwork':5,'decision':'Diterima','note':'good'},headers=csrf_headers(cs))
    assert review.status_code==200,review.text
    w=c.get('/api/records/weekly_score').json()['items']
    assert len(w)==1 and w[0]['weighted_score']>=85
    assert c.post('/api/records/weekly_score',json={'unit':'WR II','data':{'weighted_score':100}},headers=csrf_headers(cs)).status_code==404
    ok=c.post(f'/api/taiwan/{alt["id"]}/decision',json={'version':alt['version'],'approve':True},headers=csrf_headers(cs))
    assert ok.status_code==200,ok.text


def test_international_request_rejects_unverified_flags(client):
    c=client;cs=login(c,'DrSteven','StrongBootstrap1!')
    c.post('/api/auth/change-password',json={'old_password':'StrongBootstrap1!','new_password':'CorrectHorseBattery1!'},headers=csrf_headers(cs))
    cs=login(c,'DrSteven','CorrectHorseBattery1!')
    r=c.post('/api/records/taiwan_application',json={'unit':'WR I','data':{'student_id':'xx','partner':'MCUT','program_type':'3+2','contribution_path':'Referensi','academics_confirmed':'false','partner_requirements_confirmed':'true'}},headers=csrf_headers(cs))
    assert r.status_code==400,r.text


def test_operator_can_prepare_event_only_own_unit(client):
    c=client;cs=login(c,'DrSteven','StrongBootstrap1!')
    c.post('/api/auth/change-password',json={'old_password':'StrongBootstrap1!','new_password':'CorrectHorseBattery1!'},headers=csrf_headers(cs))
    cs=login(c,'DrSteven','CorrectHorseBattery1!')
    resp=c.post('/api/users',json={'username':'OperatorWR1','display_name':'Operator Akademik','role':'operator','unit':'WR I'},headers=csrf_headers(cs))
    pwd=resp.json()['temporary_password']
    cs=login(c,'OperatorWR1',pwd)
    c.post('/api/auth/change-password',json={'old_password':pwd,'new_password':'NewOperatorSecure234!'},headers=csrf_headers(cs))
    cs=login(c,'OperatorWR1','NewOperatorSecure234!')
    req=c.post('/api/records/event',json={'unit':'WR I','data':{'name':'Workshop Mahasiswa','date':'2027-09-17','pic':'Operator'}},headers=csrf_headers(cs))
    assert req.status_code==200,req.text
    event=req.json()['item']
    forbidden=c.patch(f'/api/records/event/{event["id"]}',json={'version':event['version'],'data':{'status':'Disetujui'}},headers=csrf_headers(cs))
    assert forbidden.status_code==403,forbidden.text
    assert c.post('/api/records/campaign',json={'unit':'WR II','data':{'name':'Konten'}},headers=csrf_headers(cs)).status_code==403
    assert c.get('/api/records/event').json()['items']
    assert c.get('/api/records/campaign').json()['items']==[]
