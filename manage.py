"""Initial server setup: run locally or inside a private container terminal."""
from __future__ import annotations
import argparse,secrets,getpass,os,pathlib,sys
from backend.database import init_db,connect,now,uid,db_backup,data_dir
from backend.security import hash_password,password_ok

p=argparse.ArgumentParser(description='CSC-MS secure server administration')
s=p.add_subparsers(dest='command',required=True)
a=s.add_parser('bootstrap-admin',help='Create first Rector account; temporary password must be changed at login.')
a.add_argument('--username',default='DrSteven')
a.add_argument('--display-name',default='Dr. Steven — Rektor ITB Carnegie')
a.add_argument('--allow-weak-local',action='store_true',help='ONLY ON OFFLINE LOCALHOST; never internet production.')
b=s.add_parser('backup',help='Create consistent SQLite backup.')
b.add_argument('--output',default='')
args=p.parse_args();init_db()
if args.command=='bootstrap-admin':
    if os.getenv('CSC_ENV','development')=='production' and args.allow_weak_local:
        sys.exit('Dilarang menggunakan bootstrap password lemah di server produksi.')
    with connect() as c:
        if c.execute("SELECT count(*) n FROM users WHERE role='admin'").fetchone()['n']:
            sys.exit('Akun admin sudah ada. Gunakan menu Manajemen Akun untuk pengguna berikutnya.')
    supplied=os.getenv('CSC_BOOTSTRAP_PASSWORD')
    if not supplied:
        supplied=secrets.token_urlsafe(18)+'A1!'
        print('PASSWORD SEMENTARA (catat dengan aman, hanya ditampilkan sekali):',supplied)
    if not password_ok(supplied):
        if not(args.allow_weak_local and supplied=='123456' and os.getenv('CSC_ENV','development')=='development'):
            sys.exit('Password sementara harus kuat. 123456 hanya diperbolehkan pada setup offline lokal.')
        print('PERINGATAN: PASSWORD LEMAH; JANGAN EKSPOS APLIKASI KE INTERNET SEBELUM DIGANTI.')
    with connect() as c:
        c.execute('INSERT INTO users VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
                  (uid('USR'),args.username,args.display_name,'','admin','ALL',hash_password(supplied),1,1,0,None,now(),now()))
    print('Admin dibuat. Username:',args.username,'Wajib ganti password saat login pertama.')
elif args.command=='backup':
    name=args.output or str(data_dir()/('backup-'+now().split('T')[0]+'.sqlite3'))
    pathlib.Path(name).parent.mkdir(parents=True,exist_ok=True)
    db_backup(name);print('Backup tersimpan:',name)
