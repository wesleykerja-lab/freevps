/* CSC-MS WEB — authenticated production frontend; all data via backend, no demo localStorage. */
(()=>{
'use strict';
const $=s=>document.querySelector(s);
const iconPaths={
 layout:'<rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/>',
 calendar:'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/><path d="M8 14h.01M12 14h.01M16 14h.01M8 18h.01M12 18h.01"/>',
 megaphone:'<path d="M3 11v2a2 2 0 0 0 2 2h2l2 5h3l-2-5h2l8 4V5l-8 4H5a2 2 0 0 0-2 2Z"/>',
 clipboard:'<rect x="5" y="4" width="14" height="17" rx="2"/><rect x="9" y="2" width="6" height="4" rx="1"/><path d="M9 12h6M9 16h6"/>',
 check:'<path d="m5 12 4 4L19 6"/><path d="M20 13v7H4V4h12"/>',
 clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 users:'<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
 graduation:'<path d="m2 10 10-5 10 5-10 5-10-5Z"/><path d="M6 12v5c2 2 10 2 12 0v-5M22 10v6"/>',
 inbox:'<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 13h5l2 3h4l2-3h5"/>',
 book:'<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z"/>',
 history:'<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5M12 7v5l4 2"/>',
 settings:'<circle cx="12" cy="12" r="3"/><path d="m19.4 15 .1.1 1.2.9-1.5 2.5-1.5-.6a8 8 0 0 1-1.7 1l-.3 1.6h-3l-.3-1.6a8 8 0 0 1-1.7-1l-1.5.6L7.7 16l1.2-.9a8 8 0 0 1 0-2l-1.2-.9 1.5-2.5 1.5.6a8 8 0 0 1 1.7-1l.3-1.6h3l.3 1.6a8 8 0 0 1 1.7 1l1.5-.6 1.5 2.5-1.2.9a8 8 0 0 1 0 2Z" transform="translate(-2 -2)"/>',
 chevron:'<path d="m9 18 6-6-6-6"/>',
 plus:'<path d="M12 5v14M5 12h14"/>',
 search:'<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
 arrow:'<path d="M5 12h14m-6-6 6 6-6 6"/>',
 down:'<path d="m6 9 6 6 6-6"/>',
 bell:'<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4"/>',
 shield:'<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/>',
 alert:'<path d="M12 3 2 21h20L12 3Z"/><path d="M12 9v5M12 18h.01"/>',
 file:'<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M8 13h8M8 17h8"/>',
 chart:'<path d="M3 3v18h18M7 16v-4M12 16V7M17 16v-7"/>',
 pen:'<path d="M12 20h9"/><path d="m16 4 4 4-11 11-5 1 1-5L16 4Z"/>',
 eye:'<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
 upload:'<path d="M12 16V3M7 8l5-5 5 5"/><path d="M4 16v4h16v-4"/>',
 close:'<path d="M5 5l14 14M19 5 5 19"/>',
 menu:'<path d="M4 6h16M4 12h16M4 18h16"/>',
 link:'<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
 wallet:'<rect x="2" y="5" width="20" height="16" rx="2"/><path d="M2 9h20M16 15h2"/>',
 external:'<path d="M14 3h7v7M21 3 10 14"/><path d="M21 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h6"/>',
 filter:'<path d="M4 7h16M7 12h10M10 17h4"/>',
 help:'<circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 1 1 5.8 1c-.7 1-2.9 1.6-2.9 3M12 17h.01"/>'
};
function icon(name,cls='ico'){return `<svg class="${cls}" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${iconPaths[name]||iconPaths.file}</svg>`;}
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

const roles={admin:'Rektor / Admin',wri:'Wakil Rektor I',wrii:'Wakil Rektor II',wriii:'Wakil Rektor III',operator:'Operator',reviewer:'PIC / Reviewer',pmb:'Penerimaan Mahasiswa Baru',finance:'Bagian Keuangan'};
const modules=[
 {id:'dashboard',title:'Dashboard Utama',icon:'layout',roles:'all'},
 {cap:'RUANG KERJA'},
 {id:'events',title:'Kegiatan WR I',icon:'calendar',roles:['admin','wri']},
 {id:'campaigns',title:'Marketing WR II',icon:'megaphone',roles:['admin','wrii']},
 {id:'tasks',title:'Penugasan Mahasiswa',icon:'clipboard',roles:['admin','wri','wrii','wriii','operator','reviewer']},
 {id:'attendance',title:'Absensi & Dispensasi',icon:'clock',roles:['admin','wri','wrii','wriii','operator']},
 {id:'referrals',title:'Referensi Mahasiswa Baru',icon:'users',roles:['admin','wrii','pmb','finance']},
 {id:'taiwan',title:'Program Taiwan',icon:'graduation',roles:['admin','wri','wrii']},
 {id:'weekly_scores',title:'Penilaian Mingguan',icon:'chart',roles:['admin','wri','wrii','wriii','operator','reviewer']},
 {id:'exemptions',title:'Pembebasan Sabtu',icon:'shield',roles:['admin','wrii','pmb','finance']},
 {cap:'MANAJEMEN'},
 {id:'students',title:'Data Mahasiswa',icon:'users',roles:['admin','wri','wrii']},
 {id:'scholarships',title:'Beasiswa',icon:'graduation',roles:['admin','wri','wrii']},
 {id:'annual_reviews',title:'Evaluasi Tahunan',icon:'chart',roles:['admin','wri','wrii']},
 {id:'sops',title:'SOP & Dokumen',icon:'book',roles:'all'},
 {id:'users',title:'Manajemen Akun',icon:'settings',roles:['admin']},
 {id:'audit',title:'Jejak Aktivitas',icon:'history',roles:['admin']},
 {id:'integrations',title:'Google & Pengaturan',icon:'link',roles:['admin']}
];
const cfg={
 weekly_scores:{api:'weekly_score',title:'Penilaian Mingguan',subtitle:'Riwayat QC yang dihasilkan otomatis dari pemeriksaan bukti tugas mahasiswa.',fields:[]},
 taiwan:{api:'taiwan_application',title:'Pengajuan Program Taiwan',subtitle:'Exchange Shih Hsin, Shih Chien, NCUE atau program 3+2 MCUT.',unit:'WR I',fields:[
 ['student_id','Mahasiswa','student','required'],['partner','Universitas Taiwan','select',['Shih Hsin University','Shih Chien University','NCUE','MCUT']],
 ['program_type','Jenis program','select',['Student Exchange','3+2']],['contribution_path','Jalur kontribusi','select',['Referensi','Kontribusi Strategis','Proyek Khusus']],
 ['referral_id','ID referensi terverifikasi (jalur A)','text'],['alternative_task_id','ID tugas diterima QC ≥85 (jalur B/C)','text'],
 ['gpa','IPK','number'],['language_level','Kemampuan bahasa','text'],
 ['academics_confirmed','Syarat akademik diperiksa WR I','select',['true','false']],
 ['partner_requirements_confirmed','Persyaratan program mitra diperiksa','select',['true','false']],['notes','Catatan pengajuan','textarea'] ]},
 students:{api:'student',title:'Data Mahasiswa',subtitle:'Register mahasiswa dan program studi.',fields:[
  ['name','Nama lengkap','text','required'],['nim','NIM / nomor registrasi','text'],['program','Program studi','select',['Teknologi Informasi','Sistem Informasi','Kewirausahaan']],
  ['cohort','Angkatan','text'],['email','Email','email'],['status','Status','select',['Aktif','Tidak Aktif','Lulus']]]},
 scholarships:{api:'scholarship',title:'Beasiswa Mahasiswa',subtitle:'Persentase 100%, 70%, atau 50% hanya berlaku untuk satu tahun akademik.',fields:[
  ['student_id','Mahasiswa','student','required'],['academic_year','Tahun akademik','text','required'],['tier','Kategori beasiswa (%)','select',['50','70','100']],
  ['start_date','Tanggal mulai','date','required'],['end_date','Tanggal berakhir','date','required'],['sk_number','Nomor SK','text'],['status','Status','select',['Aktif','Selesai','Dibatalkan']]]},
 events:{api:'event',title:'Kegiatan Mahasiswa · WR I',subtitle:'Kalender seminar, Imlek, event mahasiswa, kepemimpinan, dan laporan kegiatan.',unit:'WR I',fields:[
  ['name','Nama acara','text','required'],['category','Kategori','select',['Seminar','Workshop','Imlek','Summer Camp','Di Zi Gui','YAWP','Student Showcase','Charity','Kompetisi','Lainnya']],
  ['objective','Tujuan pembelajaran dan karakter','textarea'],['date','Tanggal mulai','date','required'],['end_date','Tanggal selesai','date'],
  ['pic','PIC kegiatan','text','required'],['target_attendees','Target peserta','number'],['budget','Rencana anggaran (Rp)','number'],
  ['status','Status acara','select',['Perencanaan','Diajukan','Disetujui','Terlaksana','Evaluasi','Selesai']],['notes','Catatan / AAR','textarea']]},
 campaigns:{api:'campaign',title:'Marketing & Sales · WR II',subtitle:'Kampanye, konten, story, feed, expo, presentasi, dan calon mahasiswa.',unit:'WR II',fields:[
  ['name','Nama kampanye','text','required'],['month','Bulan kampanye (YYYY-MM)','month','required'],
  ['audience','Audiens sasaran','text'],['message','Pesan utama / brief','textarea'],['target','Target output konten','number'],
  ['delivered','Output selesai','number'],['pic','PIC Marketing','text','required'],['status','Status','select',['Rencana','Aktif','Evaluasi','Selesai']]]},
 tasks:{api:'task',title:'Penugasan Mahasiswa',subtitle:'Tugas harus punya target, PIC, tenggat, dan bukti sebelum diterima.',fields:[
  ['unit','Unit penanggung jawab','unit','required'],['student_id','Mahasiswa','student','required'],
  ['title','Judul penugasan','text','required'],['category','Jenis kontribusi','select',['Konten Video','Story/Feed','Expo','Presentasi','Event','Seminar','Charity','IT/Website','Olahraga','Lainnya']],
  ['brief','Instruksi / brief','textarea'],['target','Output yang wajib diserahkan','textarea'],['acceptance_criteria','Kriteria diterima / QC','textarea'],
  ['date','Tanggal tugas','date'],['due_date','Tenggat','date','required'],['pic','PIC / reviewer','text','required'],
  ['status','Status','select',['Ditugaskan','Dalam Proses','Menunggu QC','Perlu Revisi','Dibatalkan']]]},
 attendance:{api:'attendance',title:'Absensi & Dispensasi',subtitle:'Pembebasan Sabtu resmi tidak dihitung sebagai mangkir.',fields:[
  ['unit','Unit kegiatan','unit','required'],['student_id','Mahasiswa','student','required'],['task_id','ID tugas (opsional)','text'],
  ['date','Tanggal','date','required'],['status','Kehadiran','select',['Hadir','Izin Disetujui','Tugas Pengganti','Pembebasan Sabtu','Tidak Hadir']],
  ['reason','Alasan / bukti dispensasi','textarea']]},
 referrals:{api:'referral',title:'Referensi Mahasiswa Baru',subtitle:'Verifikasi berlapis oleh PMB dan Keuangan; tidak cukup hanya memberikan nomor kontak.',unit:'WR II',fields:[
  ['referrer_student_id','Mahasiswa pemberi referensi','student','required'],['new_student_name','Nama mahasiswa baru','text','required'],
  ['new_student_id','Nomor daftar ulang/NIM','text'],['admission_record_id','ID PMB (opsional)','text'],['attribution_note','Bukti sumber referensi','textarea'],['notes','Keterangan','textarea']]},
 annual_reviews:{api:'annual_review',title:'Evaluasi Tahunan Beasiswa',subtitle:'Bobot 60% kontribusi, 25% akademik, 15% karakter. Keputusan akhir hanya Rektor.',unit:'WR I',fields:[
  ['student_id','Mahasiswa','student','required'],['academic_year','Tahun akademik','text','required'],['gpa','IPK kumulatif','number','required'],
  ['contribution_score','Skor kontribusi (0–100)','number','required'],['academic_score','Skor akademik (0–100)','number','required'],
  ['character_score','Skor karakter (0–100)','number','required'],['requested_tier','Kategori yang diajukan (%)','select',['0','50','70','100']],
  ['recommended_tier','Rekomendasi (%)','select',['0','50','70','100']]]}
};
let currentUser=null,csrf='',page='dashboard',appData={},pageData=[],modal=null,navOpen=false,loadingPage=false;
const app=$('#app');
function msg(e){return e?.detail||e?.message||String(e||'Terjadi kesalahan');}
async function api(path,{method='GET',body,upload}={}){
 let opt={method,credentials:'same-origin',headers:{'Accept':'application/json'}};
 if(method!=='GET')opt.headers['X-CSRF-Token']=csrf;
 if(upload){opt.body=upload;}else if(body!==undefined){opt.headers['Content-Type']='application/json';opt.body=JSON.stringify(body);}
 const r=await fetch('/api/'+path.replace(/^\//,''),opt);
 let json={};try{json=await r.json();}catch(e){}
 if(!r.ok){if(r.status===401&&path!=='auth/login')return sessionLost();throw new Error(msg(json));}
 return json;
}
function sessionLost(){currentUser=null;csrf='';renderLogin('Sesi berakhir. Silakan masuk kembali.');throw new Error('Sesi habis.');}
function toast(text,warning=false){document.querySelector('#toast')?.remove();const el=document.createElement('div');el.id='toast';el.className='toast'+(warning?' warn':'');el.textContent=text;document.body.append(el);setTimeout(()=>el.remove(),4600);}
function role(){return currentUser?.role||'guest';}
function permitted(p){const m=modules.find(x=>x.id===p);if(!m)return false;if(role()==='operator'&&p==='events'&&currentUser.unit==='WR I')return true;if(role()==='operator'&&p==='campaigns'&&currentUser.unit==='WR II')return true;return m.roles==='all'||m.roles.includes(role());}
function canCreate(){return role()==='admin'||({events:['wri',...(currentUser?.unit==='WR I'?['operator']:[])],campaigns:['wrii',...(currentUser?.unit==='WR II'?['operator']:[])],tasks:['wri','wrii','wriii','operator'],attendance:['wri','wrii','wriii','operator'],referrals:['wrii','pmb'],students:['wri'],annual_reviews:['wri'],taiwan:['wri','wrii']}[page]||[]).includes(role());}
function canEdit(rec){if(role()==='admin')return true;if(role()==='wri')return ['events','students','annual_reviews','taiwan','tasks','attendance'].includes(page)&&(!rec.unit||rec.unit==='WR I');if(role()==='wrii')return ['campaigns','taiwan','tasks','attendance','referrals'].includes(page)&&(!rec.unit||rec.unit==='WR II');if(role()==='wriii')return ['tasks','attendance'].includes(page)&&rec.unit==='WR III';if(role()==='operator')return ['tasks','attendance','events','campaigns'].includes(page)&&rec.unit===currentUser.unit;return false;}
const iconName={dashboard:'layout',events:'calendar',campaigns:'megaphone',tasks:'clipboard',attendance:'clock',students:'users',scholarships:'graduation',referrals:'users',exemptions:'shield',taiwan:'graduation',weekly_scores:'chart',annual_reviews:'chart',sops:'book',users:'settings',audit:'history',integrations:'link'};
function side(){return `<aside id="sidebar" class="sidebar ${navOpen?'open':''}"><div class="brand"><div class="brand-mark">C</div><div><div class="brand-name">CARNEGIE</div><div class="brand-sub">CAMPUS OPERATIONS</div></div></div><nav class="nav">${modules.map(m=>m.cap?`<div class="nav-cap">${m.cap}</div>`:permitted(m.id)?`<button class="nav-item ${page===m.id?'active':''}" data-nav="${m.id}">${icon(m.icon)}<span>${esc(m.title)}</span></button>`:'').join('')}</nav><div class="sidebar-foot"><div class="sidebar-help"><strong>Satu sistem, dua fokus</strong><div class="tiny">WR I: akademik & event.<br>WR II: marketing & kontribusi.<br>Rektor: keputusan & audit.</div><button class="small-link" data-nav="sops" style="border:0;background:none;padding:0">Lihat SOP ${icon('arrow')}</button></div><div class="sidebar-footerline"><span><i class="statusdot"></i>Database aktif</span><span>Web 1.0</span></div></div></aside>`;}
function top(){return `<header class="topbar"><div class="top-left"><button class="mobile-menu" data-act="nav-toggle" aria-label="Buka menu">${icon('menu')}</button><span class="crumb">CSC-MS &nbsp;/&nbsp; <strong>${esc(modules.find(m=>m.id===page)?.title||'Dashboard')}</strong></span><span class="top-divider"></span><span class="top-motto">ITB Carnegie · Sistem Kontribusi Terintegrasi</span></div><div class="top-right"><span class="badge-live">PORTAL AKTIF</span><div class="top-user"><div><div class="user-name">${esc(currentUser.display_name)}</div><small>${esc(roles[role()])}</small></div><span class="avatar">${esc((currentUser.display_name||'U').slice(0,1).toUpperCase())}</span></div><button class="btn small" data-act="change-password" title="Ganti password">${icon('shield')}</button><button class="btn small" data-act="logout" title="Keluar">Keluar</button></div></header>`;}
function shell(inner){app.innerHTML=`<div class="app-shell">${side()}<div class="main-area">${top()}<main class="content page-shell">${inner}</main></div></div><div class="mobile-shade ${navOpen?'open':''}" data-act="nav-toggle"></div>`;}
function heading(title,sub,actions=''){return `<div class="heading-row"><div><p class="eyebrow">ITB CARNEGIE · 2027 / 2028</p><h1 class="page-title">${esc(title)}</h1><p class="page-sub">${esc(sub)}</p></div>${actions?`<div class="heading-actions">${actions}</div>`:''}</div>`;}
function button(action,label,extra=''){return `<button type="button" class="btn ${extra}" data-act="${action}">${label}</button>`;}
function status(v){const val=String(v||'—');let cl=/Disetujui|Diterima|Selesai|Terverifikasi|Aktif|Hadir/.test(val)?'green':/Revisi|Menunggu|Pending|Evaluasi|Perencanaan|Rencana/.test(val)?'amber':/Ditolak|Dibatalkan|Tidak/.test(val)?'rose':'blue';return `<span class="pill ${cl}">${esc(val)}</span>`;}
function val(x){return x===undefined||x===null||x===''?'—':esc(x);}
function fmt(x){if(!x)return '—';let d=new Date(String(x).length===10?x+'T12:00:00':x);return isNaN(d)?esc(x):new Intl.DateTimeFormat('id-ID',{day:'2-digit',month:'short',year:'numeric'}).format(d);}
function monthNow(){return new Date().toISOString().slice(0,7);}
function renderLogin(error=''){
 app.innerHTML=`<section class="auth-shell"><div class="auth-side"><div class="auth-brand"><div class="auth-mark">C</div><div><h2>CARNEGIE</h2><p>SCHOLARSHIP & ACTIVITY PORTAL</p></div></div><div><div class="auth-tag">CAMPUS OPERATIONS</div><h2 class="auth-heading">Satu ruang kerja.<br>Satu standar.<br>Hasil yang terukur.</h2><p class="auth-desc">Mengelola kegiatan akademik, kontribusi mahasiswa, kampanye marketing, bukti pekerjaan, dan evaluasi beasiswa secara transparan.</p></div><footer>INSTITUT TEKNOLOGI DAN BISNIS CARNEGIE · MEDAN</footer></div><div class="auth-main"><div class="auth-card"><div class="mini-head">AKSES TERBATAS · STAF ITB CARNEGIE</div><h1>Selamat datang</h1><p>Masuk dengan akun pribadi yang diberikan oleh Administrator.</p>${error?`<div class="auth-error" role="alert">${esc(error)}</div>`:''}<form class="auth-form" id="login-form"><label>Username<input type="text" name="username" maxlength="60" autocomplete="username" placeholder="Username" required autofocus></label><label>Password<input type="password" name="password" autocomplete="current-password" required placeholder="Password sementara / pribadi"></label><button class="btn primary" type="submit">Masuk ke Portal ${icon('arrow')}</button></form><div class="auth-secure">${icon('shield')} Akses tercatat dan dilindungi; password sementara wajib diganti.</div></div></div></section>`;
}
function renderChange(error=''){
 app.innerHTML=`<section class="auth-shell"><div class="auth-side"><div class="auth-brand"><div class="auth-mark">C</div><div><h2>CARNEGIE</h2><p>ACCOUNT SECURITY</p></div></div><div><div class="auth-tag">KEAMANAN AKUN</div><h2 class="auth-heading">Password pribadi.<br>Akses lebih aman.</h2><p class="auth-desc">Setiap anggota WR I, WR II, WR III dan operator wajib mengubah password sementara saat masuk pertama kali.</p></div><footer>CSC-MS · ITB CARNEGIE</footer></div><div class="auth-main"><div class="auth-card"><div class="mini-head">PERTAMA KALI MASUK</div><h1>Ganti password wajib</h1><p>Minimal 12 karakter, gabungan sedikitnya tiga unsur: huruf besar, huruf kecil, angka, dan simbol.</p>${error?`<div class="auth-error">${esc(error)}</div>`:''}<form id="password-form" class="auth-form"><label>Password lama / sementara<input type="password" name="old_password" autocomplete="current-password" required></label><label>Password baru<input type="password" name="new_password" autocomplete="new-password" minlength="12" required></label><label>Konfirmasi password baru<input type="password" name="confirm_password" autocomplete="new-password" minlength="12" required></label><button class="btn primary" type="submit">Simpan Password Baru</button></form><div class="auth-secure">${icon('shield')} Setelah berhasil, silakan masuk kembali menggunakan password baru.</div></div></div></section>`;
}
async function bootstrap(){try{const resp=await api('me');currentUser=resp.user;csrf=resp.csrf;if(currentUser.must_change)renderChange();else await navigate('dashboard');}catch(e){if(!currentUser)renderLogin();}}
async function navigate(p){if(!permitted(p))return toast('Menu tidak tersedia untuk jabatan Anda.',true);page=p;navOpen=false;modal=null;shell(heading('Memuat data…','Menghubungkan ke database kampus.'));try{if(p==='dashboard')await dashboard();else if(p==='sops')await renderSops();else if(p==='users')await renderUsers();else if(p==='audit')await renderAudit();else if(p==='integrations')await renderIntegrations();else if(p==='exemptions')await renderExemptions();else if(p==='weekly_scores')await renderWeeklyScores();else await renderRecords(p);}catch(e){shell(heading('Tidak bisa memuat halaman',msg(e))+`<div class="status-line">Periksa koneksi server atau hak akses akun Anda.</div>`);toast(msg(e),true);}}
function card(label,number,note,ico,cl=''){return `<div class="kpi ${cl}"><div class="kpi-icon">${icon(ico)}</div><div class="kpi-cap">${esc(label)}</div><div class="kpi-val numeric">${esc(number)}</div><div class="kpi-foot">${esc(note)}</div></div>`;}
function rowOf(items,formatter,empty='Belum ada data pada periode ini.'){
 if(!items.length)return `<div class="empty-state"><h3>Belum ada aktivitas</h3><p>${esc(empty)}</p></div>`;
 return `<ul class="list-plain">${items.map(formatter).join('')}</ul>`;
}
async function dashboard(){
 const d=await api('dashboard');const c=d.counts||{};
 const r=role(),admin=r==='admin',wri=r==='wri',wrii=r==='wrii';
 const title=admin?'Dashboard Rektor / Admin':wri?'Dashboard WR I — Akademik & Kegiatan':wrii?'Dashboard WR II — Marketing & Sales':`Dashboard ${roles[r]}`;
 const desc=admin?'Memantau hasil kerja WR I, WR II, kontribusi mahasiswa, bukti, dan keputusan beasiswa.':wri?'Pimpin seminar, Imlek, event mahasiswa, kepemimpinan, dan proyek akademik.':wrii?'Kelola konten, feed, story, expo, presentasi, serta referensi mahasiswa baru.':'Pekerjaan, bukti, dan persetujuan sesuai hak akses akun.';
 const hero=admin?'Semua kegiatan terlihat.<br>Setiap hasil dapat dibuktikan.':wri?'Aktifkan kegiatan.<br>Bangun karakter mahasiswa.':wrii?'Dari ide menjadi karya.<br>Dari karya menjadi dampak.':'Tugas jelas.<br>Bukti lengkap. Evaluasi adil.';
 let action=(admin||wri||wrii)?`<button class="btn primary" data-nav="${admin?'tasks':wri?'events':'campaigns'}">${icon('plus')} ${admin?'Kelola Tugas':wri?'Buat Kegiatan':'Buat Kampanye'}</button>`:'';
 const tasks=(d.recent_tasks||[]),events=(d.recent_events||[]),campaigns=(d.recent_campaigns||[]);
 let stats=admin?[
  ['Mahasiswa tercatat',c.student||0,'Data register mahasiswa','users',''],
  ['Tugas diterima QC',d.accepted_tasks||0,'Bukti telah diverifikasi PIC','check','blue'],
  ['Menunggu Quality Control',d.pending_qc||0,'Butuh tindakan supervisor','clock','amber'],
  ['Evaluasi menunggu Rektor',d.pending_annual||0,'Keputusan perpanjangan / kategori','shield','rose']
 ]:[
  [wri?'Total kegiatan WR I':wrii?'Kampanye WR II':'Total tugas unit',wri?c.event||0:wrii?c.campaign||0:c.task||0,'Record operasional yang tersedia',wri?'calendar':wrii?'megaphone':'clipboard',''],
  ['Tugas diterima QC',d.accepted_tasks||0,'Hasil selesai dan disetujui','check','blue'],
  ['Bukti menunggu QC',d.pending_qc||0,'Perlu diperiksa supervisor','clock','amber'],
  ['Tugas lewat tenggat',d.overdue_tasks||0,'Periksa kendala kampus/mahasiswa','alert','rose']
 ];
 shell(`${heading(title,desc,action)}<section class="hero"><div><div class="hero-cap">${admin?'REKTOR · ADMINISTRASI':wri?'AKADEMIK · KEMAHASISWAAN':wrii?'KONTEN · EXPO · PMB':'OPERASIONAL HARIAN'}</div><h2>${hero}</h2><p>Tidak cukup absensi. Setiap tugas memiliki PIC, tenggat, bukti, pemeriksaan kualitas, dan hasil yang bisa dipertanggungjawabkan.</p></div><div class="hero-right"><div class="hero-year">2027<span> / 2028</span></div><div class="hero-pill">Ruang kerja: ${esc(roles[r])}</div></div></section>
 <section class="kpi-grid">${stats.map(x=>card(...x)).join('')}</section>
 <section class="dashboard-grid"><div class="panel"><div class="panel-head"><div><h3 class="panel-title">${admin?'Perbandingan Kinerja WR I & WR II':wri?'Agenda Kegiatan Mahasiswa':wrii?'Kampanye Marketing & Konten':'Tugas Terbaru'}</h3><div class="panel-sub">${admin?'Kegiatan dan kampanye dicatat terpisah menurut penanggung jawab.':'Kegiatan dari rencana hingga bukti selesai dan diterima.'}</div></div></div>
 ${admin?`<div class="unit-columns"><div class="unit-card"><div class="unit-top"><span class="unit-label">WR I · KEGIATAN</span>${icon('calendar')}</div><div class="unit-number">${c.event||0}</div><div class="unit-desc">Seminar, Imlek, event mahasiswa, kepemimpinan.</div><div class="unit-bottom"><button class="link-action" data-nav="events">Lihat kegiatan ${icon('chevron')}</button></div></div><div class="unit-card"><div class="unit-top"><span class="unit-label">WR II · MARKETING</span>${icon('megaphone')}</div><div class="unit-number">${c.campaign||0}</div><div class="unit-desc">Konten, story, expo, presentasi dan PMB.</div><div class="unit-bottom"><button class="link-action" data-nav="campaigns">Lihat kampanye ${icon('chevron')}</button></div></div></div>`:
 wri?`<div class="need-action">${rowOf(events,e=>`<li><div><strong>${esc(e.name)}</strong><div class="small-text">${fmt(e.date)} · ${esc(e.pic)}</div></div>${status(e.status)}</li>`,'Belum ada kegiatan WR I. Susun kalender dan proposal kegiatan mahasiswa.')}</div>`:
 wrii?`<div class="need-action">${rowOf(campaigns,e=>`<li><div><strong>${esc(e.name)}</strong><div class="small-text">${esc(e.month||'')} · ${esc(e.pic)}</div></div>${status(e.status)}</li>`,'Belum ada kampanye WR II. Buat brief dan target mingguan.')}</div>`:
 `<div class="need-action">${rowOf(tasks,e=>`<li><div><strong>${esc(e.title)}</strong><div class="small-text">${esc(e.unit)} · ${fmt(e.due_date)}</div></div>${status(e.status)}</li>`)}</div>`}</div>
 <div class="panel"><div class="panel-head"><div><h3 class="panel-title">Hal yang Perlu Ditindaklanjuti</h3><div class="panel-sub">Pemantauan mingguan, bukan formalitas absensi.</div></div></div><div class="need-action"><ul class="list-plain">
 <li><div><strong>${d.pending_qc||0} bukti menunggu QC</strong><div class="small-text">Supervisor wajib menerima atau meminta revisi secara tertulis.</div></div>${icon('clock')}</li>
 <li><div><strong>${d.overdue_tasks||0} tugas melewati tenggat</strong><div class="small-text">Pastikan penyebabnya bukan brief yang terlambat dari kampus.</div></div>${icon('alert')}</li>
 <li><div><strong>${admin?'Rektor: evaluasi akhir tahun':wri?'WR I: minimal 1 event/bulan aktif':wrii?'WR II: brief konten mingguan':'Pencatatan bukti yang sah'}</strong><div class="small-text">Tetapkan PIC, jadwal, hasil, dan after-action report.</div></div>${icon('clipboard')}</li>
 <li><div><strong>SOP & Dokumen</strong><div class="small-text">Akses kebijakan yang sudah disahkan dan panduan kerja.</div></div><button class="table-action" data-nav="sops">Buka</button></li></ul></div></div></section>
 <section class="panel"><div class="panel-head"><div><h3 class="panel-title">Penugasan Terbaru</h3><div class="panel-sub">Data langsung dari server kampus.</div></div><button class="link-action" data-nav="tasks">Lihat tugas ${icon('chevron')}</button></div>
 <div class="need-action">${rowOf(tasks.slice(0,6),t=>`<li><div><strong>${esc(t.title)}</strong><div class="small-text">${esc(t.unit)} · PIC ${esc(t.pic)} · Tenggat ${fmt(t.due_date)}</div></div>${status(t.status)}</li>`,'Belum ada penugasan. Silakan masukkan mahasiswa lalu buat tugas dengan target dan PIC.')}</div></section>`);
}
function summaryColumn(page,o){
 if(page==='students')return [o.name,o.program,o.cohort,o.status];
 if(page==='scholarships')return [studentName(o.student_id),o.academic_year,`${o.tier||0}%`,o.status];
 if(page==='events')return [o.name,fmt(o.date),o.pic,o.status];
 if(page==='campaigns')return [o.name,o.month,o.pic,o.status];
 if(page==='tasks')return [o.title,`${o.unit} · ${studentName(o.student_id)}`,fmt(o.due_date),o.status];
 if(page==='attendance')return [studentName(o.student_id),fmt(o.date),o.unit,o.status];
 if(page==='referrals')return [studentName(o.referrer_student_id),o.new_student_name,o.payment_status,o.status];
 if(page==='annual_reviews')return [studentName(o.student_id),o.academic_year,`${o.total_score??'—'}/100`,o.status];
 if(page==='taiwan')return [studentName(o.student_id),o.partner,o.contribution_path,o.status];
 return [o.name||o.title,o.unit||'—',o.status||'—',o.id];
}
function headings(page){return {
 students:['Nama','Program Studi','Angkatan','Status'],scholarships:['Mahasiswa','TA','Potongan','Status'],
 events:['Nama Acara','Tanggal','PIC','Status'],campaigns:['Kampanye','Periode','PIC','Status'],tasks:['Tugas','Unit / Mahasiswa','Tenggat','Status'],
 attendance:['Mahasiswa','Tanggal','Unit','Status'],referrals:['Pemberi Referensi','Mahasiswa Baru','Pembayaran','Verifikasi'],
 annual_reviews:['Mahasiswa','TA','Skor Akhir','Status'],taiwan:['Mahasiswa','Perguruan Tinggi','Jalur Kontribusi','Status']
 }[page]||['Nama','Unit','Status','ID'];}
function studentName(id){let r=(appData.students||[]).find(x=>x.id===id);return r?r.name:id||'—';}
async function renderRecords(p){
 const conf=cfg[p];if(!conf)return;
 const [data,students]=await Promise.all([api(`records/${conf.api}`),p==='students'?Promise.resolve({items:[]}):api('records/student').catch(()=>({items:[]}))]);
 pageData=data.items;appData.students=p==='students'?data.items:students.items;
 let buttons=`<button class="btn" data-act="export-csv">${icon('file')} CSV</button>`;
 if(canCreate())buttons+=`<button class="btn primary" data-act="new-record">${icon('plus')} Tambah Data</button>`;
 let special='';
 if(p==='events')special=`<div class="report-grid"><div class="report-card"><h3>Target kegiatan WR I</h3><p>Usulan standar: 1 kegiatan setiap bulan perkuliahan aktif, 1 acara unggulan per semester.</p></div><div class="report-card"><h3>Acara bukan sekadar perayaan</h3><p>Setiap kegiatan wajib memiliki tujuan karakter, proposal, panitia, peserta, bukti, dan laporan evaluasi.</p></div></div>`;
 if(p==='campaigns')special=`<div class="report-grid"><div class="report-card"><h3>Target Marketing WR II</h3><p>Minimal 1 kampanye aktif per bulan, dengan brief mingguan untuk video, Reels, story, dan feed.</p></div><div class="report-card"><h3>Hasil yang harus diverifikasi</h3><p>Konten selesai melalui QC, expo dan presentasi tercatat, referensi mahasiswa baru diverifikasi PMB dan Keuangan.</p></div></div>`;
 if(p==='taiwan')special=`<div class="status-line good">Satu mahasiswa baru TERDAFTAR dan LUNAS/Terpenuhi setelah verifikasi PMB/Finance, ATAU kontribusi alternatif yang disetujui dengan QC ≥85. Tidak menjamin penerimaan Taiwan.</div>`;
 if(p==='annual_reviews')special=`<div class="status-line good">Kontribusi 60% + akademik 25% + karakter 15%. Kategori 100%: IPK ≥3,60 dan skor ≥90; 70%: IPK ≥3,25 dan skor ≥80; 50%: IPK ≥3,00 dan skor ≥70. Keputusan final hanya Rektor.</div>`;
 let rows=pageData.map(o=>`<tr data-query="${esc(JSON.stringify(o).toLowerCase())}">${summaryColumn(p,o).map((x,i)=>`<td class="${i===0?'primary-cell':''}">${i===3||p==='referrals'&&i>=2?status(x):val(x)}${i===0?`<div class="subtext">${esc(o.id)}</div>`:''}</td>`).join('')}<td><button class="table-action" data-act="view" data-id="${esc(o.id)}">Detail</button>${canEdit(o)?`<button class="table-action" data-act="edit" data-id="${esc(o.id)}">Ubah</button>`:''}</td></tr>`).join('');
 shell(`${heading(conf.title,conf.subtitle,buttons)}${special}<div class="toolbar"><input id="search-filter" type="search" placeholder="Cari nama, ID, PIC, status…" aria-label="Cari"><span class="small-text">${pageData.length} catatan ditemukan</span></div><div class="panel">${pageData.length?`<div class="table-wrap"><table class="data-table"><thead><tr>${[...headings(p),'Tindakan'].map(s=>`<th>${esc(s)}</th>`).join('')}</tr></thead><tbody>${rows}</tbody></table></div>`:`<div class="empty-state"><h3>Belum ada catatan</h3><p>Database sudah siap. Isi data melalui tombol Tambah Data agar tim dapat mulai bekerja secara terukur.</p>${canCreate()?button('new-record','Buat data pertama','primary'):''}</div>`}</div>`);
}
function fieldHtml(field,value=''){
 const [key,label,type,extra]=field,required=extra==='required';
 const attr=`name="${esc(key)}" id="fld-${esc(key)}" ${required?'required':''}`;
 const v=(value??'').toString();
 if(type==='textarea')return `<div class="field full"><label for="fld-${esc(key)}">${esc(label)}</label><textarea ${attr} rows="3">${esc(v)}</textarea></div>`;
 if(type==='select'){let opt=Array.isArray(extra)?extra:[];return `<div class="field"><label for="fld-${esc(key)}">${esc(label)}</label><select ${attr}><option value="">— Pilih —</option>${opt.map(o=>`<option value="${esc(o)}" ${String(o)===v?'selected':''}>${esc(o)}</option>`).join('')}</select></div>`;}
 if(type==='student'){let s=appData.students||[];return `<div class="field"><label for="fld-${esc(key)}">${esc(label)}</label><select ${attr}><option value="">— Pilih mahasiswa —</option>${s.map(o=>`<option value="${esc(o.id)}" ${o.id===v?'selected':''}>${esc(o.name)} · ${esc(o.program||'')}</option>`).join('')}</select></div>`;}
 if(type==='unit'){let choices=role()==='admin'?['WR I','WR II','WR III']:role()==='wri'?['WR I']:role()==='wrii'?['WR II']:role()==='wriii'?['WR III']:[currentUser.unit];
 return `<div class="field"><label for="fld-unit">${esc(label)}</label><select ${attr}>${choices.map(o=>`<option value="${esc(o)}" ${o===v?'selected':''}>${esc(o)}</option>`).join('')}</select></div>`;}
 let step=type==='number'?'step="any"':'';
 return `<div class="field"><label for="fld-${esc(key)}">${esc(label)} ${required?'*':''}</label><input ${attr} type="${type}" value="${esc(v)}" ${step} maxlength="${type==='text'?300:undefined}" placeholder="${type==='month'?'YYYY-MM':''}"></div>`;
}
function showModal(title,sub,inner,footer=''){
 modal=true;
 const div=document.createElement('div');div.className='overlay';div.id='modal-overlay';div.innerHTML=`<section class="modal wide" role="dialog" aria-modal="true" aria-labelledby="modal-h"><div class="modal-head"><div><h2 id="modal-h">${esc(title)}</h2><p>${esc(sub)}</p></div><button class="close" data-act="close-modal" aria-label="Tutup">${icon('close')}</button></div><div class="modal-body">${inner}</div>${footer?`<div class="modal-foot">${footer}</div>`:''}</section>`;
 document.body.appendChild(div);
 const el=div.querySelector('input,select,textarea,button');if(el)el.focus();
}
function closeModal(){document.getElementById('modal-overlay')?.remove();modal=null;}
function formData(form){const result={};for(const [k,v] of new FormData(form)){if(v instanceof File)continue;if(v!=='')result[k]=v;}return result;}
function formForNewOrEdit(rec=null){
 const conf=cfg[page];if(!conf)return;
 const edit=!!rec;
 let fields=conf.fields.slice();
 if(role()==='operator'&&['events','campaigns'].includes(page))fields=fields.filter(x=>x[0]!=='status');
 if(edit&&page==='scholarships')fields=fields.filter(f=>['start_date','end_date','sk_number','status'].includes(f[0]));
 if(edit&&page==='annual_reviews')fields=fields.filter(f=>!['student_id','academic_year'].includes(f[0]));
 if(edit&&page==='tasks'&&rec.status==='Diterima')return toast('Tugas yang sudah diterima QC tidak dapat diedit tanpa proses koreksi.',true);
 const markup=`<form id="record-form" class="form-stack"><div class="form-grid">${fields.map(f=>fieldHtml(f,rec?.[f[0]]|| (f[0]==='academic_year'?'2027/2028':f[0]==='month'?monthNow():f[0]==='status'?(page==='events'?'Perencanaan':page==='campaigns'?'Rencana':'Aktif') :''))).join('')}</div><div class="form-note">Setiap perubahan akan disimpan ke server dan dicatat dalam audit. Mohon isi target yang dapat dibuktikan; hindari formulir tanpa kejelasan output.</div><div class="btn-row"><button class="btn primary" type="submit">${edit?'Simpan Perubahan':'Simpan Data'}</button><button class="btn" type="button" data-act="close-modal">Batal</button></div></form>`;
 showModal(edit?'Ubah '+conf.title:'Tambah '+conf.title,edit?`ID: ${rec.id} · versi ${rec.version}`:'Formulir tersimpan sebagai record resmi. ',markup);
 document.getElementById('record-form').addEventListener('submit',async ev=>{
  ev.preventDefault();const form=ev.target,values=formData(form);
  let unit=conf.unit||values.unit||rec?.unit|| (page==='students'?'WR I':page==='scholarships'?'ADMIN':page==='annual_reviews'?'WR I':currentUser.unit);
  delete values.unit;
  for(const k of ['tier','requested_tier','recommended_tier','target','delivered','budget','target_attendees','attendees','contribution_score','academic_score','character_score','gpa'])if(k in values)values[k]=Number(values[k]);
  for(const k of ['academics_confirmed','partner_requirements_confirmed'])if(k in values)values[k]=(values[k]==='true');
  const b=form.querySelector('[type=submit]');b.disabled=true;
  try{
    await api(`records/${conf.api}${edit?'/'+rec.id:''}`,{method:edit?'PATCH':'POST',body:edit?{version:rec.version,data:values}:{unit,data:values}});
    closeModal();toast('Data disimpan di server.');await navigate(page);
  }catch(e){toast(msg(e),true);b.disabled=false;}
 });
}
async function viewRecord(id){const o=pageData.find(x=>x.id===id);if(!o)return;
 const fields=Object.entries(o).filter(([k])=>!['kind','created_at','updated_at','version','created_by','unit'].includes(k));
 const special=page==='tasks'?`<div class="divider"></div><div class="btn-row"><button class="btn primary" data-act="evidence" data-id="${esc(o.id)}">${icon('upload')} Unggah / Lihat Bukti</button>${['admin','wri','wrii','wriii','reviewer'].includes(role())?`<button class="btn" data-act="qc" data-id="${esc(o.id)}">${icon('check')} Quality Control</button>`:''}</div>`:
 page==='referrals'?`<div class="divider"></div><p class="note-blue">Pembebasan Sabtu 12 bulan hanya dapat diberikan setelah PMB dan Keuangan memverifikasi secara sah. Referensi tidak otomatis dapat dipakai dua kali untuk fasilitas Taiwan.</p><div class="btn-row">${['admin','pmb'].includes(role())?`<button class="btn" data-act="verify-pmb" data-id="${esc(o.id)}">Verifikasi PMB</button>`:''}${['admin','finance'].includes(role())?`<button class="btn" data-act="verify-finance" data-id="${esc(o.id)}">Verifikasi Keuangan</button>`:''}${['admin','wrii'].includes(role())?`<button class="btn primary" data-act="exempt" data-id="${esc(o.id)}">Setujui Pembebasan Sabtu</button>`:''}</div>`:
 page==='taiwan'&&role()==='admin'?`<div class="divider"></div><div class="btn-row"><button class="btn primary" data-act="taiwan-decision" data-id="${esc(o.id)}">Keputusan Rektor — Taiwan</button></div>`:
 page==='annual_reviews'&&role()==='admin'?`<div class="divider"></div><div class="btn-row"><button class="btn primary" data-act="annual-decision" data-id="${esc(o.id)}">Keputusan Rektor</button></div>`:'';
 const html=`<dl class="detail-rows">${fields.map(([k,v])=>`<dt>${esc(k.replaceAll('_',' '))}</dt><dd>${typeof v==='object'?esc(JSON.stringify(v)):val(v)}</dd>`).join('')}<dt>Unit</dt><dd>${val(o.unit)}</dd><dt>Versi data</dt><dd>${o.version}</dd><dt>Terakhir diubah</dt><dd>${fmt(o.updated_at)}</dd></dl>${special||''}`;
 showModal('Detail '+cfg[page].title,`ID: ${o.id}`,html);
}
async function renderExemptions(){let x=await api('records/exemption');pageData=x.items;
 shell(`${heading('Pembebasan Kegiatan Sabtu','Hanya berlaku 12 bulan sesudah verifikasi PMB dan Keuangan serta persetujuan WR II/Rektor.')}<div class="status-line good">Referensi berhasil tidak otomatis memperpanjang beasiswa. Pembebasan tidak menghapus perkuliahan, ujian, dan kewajiban expo sekolah asal yang disepakati.</div><div class="panel">${x.items.length?`<div class="table-wrap"><table class="data-table"><thead><tr><th>Mahasiswa</th><th>Referensi</th><th>Mulai</th><th>Berakhir</th><th>Status</th></tr></thead><tbody>${x.items.map(o=>`<tr><td>${esc(o.student_id||'—')}</td><td>${esc(o.referral_id||'—')}</td><td>${fmt(o.start_date)}</td><td>${fmt(o.end_date)}</td><td>${status(o.status)}</td></tr>`).join('')}</tbody></table></div>`:`<div class="empty-state"><h3>Belum ada fasilitas pembebasan</h3><p>Masuk ke Referensi Mahasiswa Baru, lakukan verifikasi PMB dan Keuangan, lalu WR II/Rektor menyetujui fasilitas secara tertulis dalam sistem.</p></div>`}</div>`);
}
async function evidenceModal(taskId){closeModal();let detail=await api(`evidence/${taskId}`);const o=(appData.tasks||pageData).find(x=>x.id===taskId);
 showModal('Bukti Kontribusi Mahasiswa',`Task ID: ${taskId} · Berkas disimpan aman pada server`,
 `<div class="form-note">Unggah foto/video/PDF/Word/Excel. Setiap file melekat ke penugasan dan tidak otomatis mendapat nilai sebelum QC. Maksimal 50 MB per berkas.</div>
 <form id="upload-form" class="form-stack"><div class="field"><label>Pilih file bukti</label><input type="file" name="file" accept=".jpg,.jpeg,.png,.webp,.pdf,.mp4,.mov,.docx,.xlsx" required></div><button class="btn primary" type="submit">Unggah dan Ajukan QC</button></form><div class="divider"></div><h3>Daftar Bukti (${detail.items.length})</h3><div>${detail.items.length?detail.items.map(x=>`<div class="file-line"><span>${esc(x.original_name)}<br><span class="small-text">${(x.size_bytes/1024).toFixed(0)} KB · ${fmt(x.created_at)}</span></span><a href="/api/evidence/file/${encodeURIComponent(x.id)}" target="_blank" rel="noopener noreferrer">Unduh</a></div>`).join(''):'<p class="small-text">Belum ada file bukti untuk tugas ini.</p>'}</div>`);
 document.getElementById('upload-form').addEventListener('submit',async ev=>{ev.preventDefault();let btn=ev.target.querySelector('button');btn.disabled=true;
 try{await api(`evidence/${taskId}/upload`,{method:'POST',upload:new FormData(ev.target)});closeModal();toast('Bukti tersimpan, status tugas menjadi Menunggu QC.');await navigate('tasks');}
 catch(e){toast(msg(e),true);btn.disabled=false;}});
}
async function qcModal(id){closeModal();const o=pageData.find(x=>x.id===id);if(!o)return;const docs=await api(`evidence/${id}`);
 showModal('Quality Control Penugasan',`Task ${id} · ${docs.items.length} bukti terunggah`,
 `<div class="form-note">Nilai 0 sampai 5 per indikator: kualitas 40%, kesesuaian target 25%, ketepatan 15%, inisiatif 10%, kerja sama 10%. Skor 0–100 dihitung di server.</div><form id="qc-form" class="form-stack"><div class="form-grid">${[['quality','Kualitas hasil'],['target','Pencapaian target'],['timeliness','Ketepatan waktu'],['initiative','Inisiatif'],['teamwork','Kerja sama']].map(([key,title])=>`<div class="field"><label>${title}</label><select name="${key}" required>${[0,1,2,3,4,5].map(n=>`<option value="${n}" ${n===3?'selected':''}>${n} / 5</option>`).join('')}</select></div>`).join('')}<div class="field"><label>Keputusan QC</label><select name="decision"><option>Diterima</option><option>Perlu Revisi</option><option>Ditolak</option></select></div><div class="field full"><label>Catatan reviewer dan tindak lanjut</label><textarea name="note" rows="3" required></textarea></div></div><button class="btn primary" type="submit">Simpan Hasil QC</button></form>`);
 document.getElementById('qc-form').addEventListener('submit',async e=>{e.preventDefault();const b=e.target.querySelector('button'),d=formData(e.target);b.disabled=true;
 for(const n of ['quality','target','timeliness','initiative','teamwork'])d[n]=Number(d[n]);d.version=o.version;
 try{await api(`tasks/${id}/review`,{method:'POST',body:d});closeModal();toast('Hasil QC tersimpan.');await navigate('tasks');}
 catch(ex){b.disabled=false;toast(msg(ex),true);}});
}
async function verifyReferral(id,type){const o=pageData.find(x=>x.id===id);if(!o)return;closeModal();let ispm=type==='pmb';
 showModal(ispm?'Verifikasi Pendaftaran PMB':'Verifikasi Pembayaran Finance',`Referensi ${id}`,
 `<div class="form-note">${ispm?'Pastikan mahasiswa baru sudah melakukan daftar ulang dan mempunyai ID resmi.':'Verifikasi uang pendaftaran DAN uang kegiatan telah lunas atau dibebaskan dengan persetujuan tertulis.'} Tidak boleh memverifikasi berdasarkan janji pembayaran.</div><form id="verify-form" class="form-stack"><label class="field-checkbox"><input type="checkbox" name="verified" checked> Saya sudah memeriksa bukti resmi dan menyatakan memenuhi syarat</label><div class="field"><label>Catatan administratif</label><textarea name="reference_note" rows="3"></textarea></div><button class="btn primary" type="submit">Simpan Verifikasi</button></form>`);
 document.getElementById('verify-form').addEventListener('submit',async e=>{e.preventDefault();let d=formData(e.target),b=e.target.querySelector('button');b.disabled=true;
 try{await api(`referrals/${id}/verify-${ispm?'pmb':'finance'}`,{method:'POST',body:{version:o.version,verified:d.verified==='on',reference_note:d.reference_note||''}});closeModal();toast('Hasil verifikasi disimpan.');await navigate('referrals');}
 catch(ex){b.disabled=false;toast(msg(ex),true);}});
}
async function exemptionModal(id){const o=pageData.find(x=>x.id===id);if(!o)return;closeModal();
 showModal('Pembebasan Kontribusi Sabtu','Berlaku 12 bulan setelah keputusan tertulis WR II / Rektor.',
 `<div class="form-note">Sistem akan menolak jika PMB atau Keuangan belum memverifikasi. Pembebasan Sabtu tidak berlaku surut dan tidak berarti seluruh kontribusi dibebaskan.</div><form id="exemption-form" class="form-stack"><div class="field"><label>Dasar persetujuan dan catatan</label><textarea name="note" rows="3" required></textarea></div><button class="btn primary" type="submit">Setujui Fasilitas 12 Bulan</button></form>`);
 document.getElementById('exemption-form').addEventListener('submit',async e=>{e.preventDefault();const btn=e.target.querySelector('button');btn.disabled=true;
 try{await api(`referrals/${id}/saturday-exemption`,{method:'POST',body:{version:o.version,approve:true,note:formData(e.target).note}});closeModal();toast('Pembebasan Sabtu disahkan dan dicatat di database.');await navigate('referrals');}
 catch(ex){btn.disabled=false;toast(msg(ex),true);}});
}
async function annualDecisionModal(id){let o=pageData.find(x=>x.id===id);if(!o)return;closeModal();
 showModal('Persetujuan Akhir Rektor',`Evaluasi ${id} · Nilai akhir: ${o.total_score}/100`,
 `<div class="form-note">SK: 100% memerlukan IPK ≥3,60 dan skor ≥90; 70% IPK ≥3,25 dan skor ≥80; 50% IPK ≥3,00 dan skor ≥70. Skor bukan satu-satunya pertimbangan; kuota dan perjanjian lama perlu diperiksa.</div><form id="decision-form" class="form-stack"><div class="form-grid"><div class="field"><label>Keputusan</label><select name="decision"><option value="yes">Setujui</option><option value="no">Tolak</option></select></div><div class="field"><label>Persentase final</label><select name="final_tier">${['0','50','70','100'].map(x=>`<option value="${x}" ${String(o.recommended_tier)===x?'selected':''}>${x}%</option>`).join('')}</select></div></div><div class="field"><label>Catatan keputusan</label><textarea name="note" rows="3"></textarea></div><button class="btn primary" type="submit">Tetapkan Keputusan Rektor</button></form>`);
 document.getElementById('decision-form').addEventListener('submit',async e=>{e.preventDefault();let d=formData(e.target),b=e.target.querySelector('button');b.disabled=true;
 try{await api(`annual-reviews/${id}/decision`,{method:'POST',body:{version:o.version,approve:d.decision==='yes',final_tier:Number(d.final_tier),note:d.note||''}});closeModal();toast('Keputusan Rektor tersimpan.');await navigate('annual_reviews');}catch(ex){b.disabled=false;toast(msg(ex),true);}});
}
async function renderSops(){
 const manuals=[
  ['SOP WR I dan WR II — Telah Disahkan','SOP-WR-I-WR-II-DISAHKAN.docx','Pembagian tanggung jawab akademik/event vs marketing/sales, alur tugas dan pembinaan.'],
  ['SOP Portal CSC-MS Versi 2.0','SOP-Portal-v2.docx','Operasional aplikasi, laporan, QC, monitoring, dan integrasi.'],
  ['Paket Formulir Kontribusi','Formulir-Kontribusi.docx','Form pembagian tugas, absensi, bukti, QC, dan evaluasi mahasiswa.']];
 shell(`${heading('SOP, Peraturan dan Pedoman','Dokumen internal tersedia bagi setiap pengguna yang berhasil login.')}
 <div class="status-line good">SOP pembagian tanggung jawab WR I dan WR II telah Anda nyatakan sah. SOP portal digital adalah panduan implementasi sistem dan tidak mengubah tanggung jawab pejabat.</div>
 <div class="doc-grid">${manuals.map(([title,file,sub])=>`<article class="doc-card"><div class="doc-icon">${icon('book')}</div><div><h3>${esc(title)}</h3><p>${esc(sub)}</p><a class="link-action" href="/api/manual/${encodeURIComponent(file)}">Download Dokumen ${icon('arrow')}</a></div></article>`).join('')}</div>`);
}
async function renderUsers(){const resp=await api('users');pageData=resp.items;
 shell(`${heading('Manajemen Akun & Hak Akses','Hanya Rektor/Admin dapat membuat username, menentukan role, reset password, dan menonaktifkan pengguna.',button('new-user',`${icon('plus')} Buat Pengguna`,'primary'))}
 <div class="status-line">Password sementara hanya tampil SATU KALI saat akun dibuat atau di-reset. Pengguna wajib mengganti password saat pertama masuk. Jangan membagikan password lewat grup publik.</div>
 <div class="panel"><div class="table-wrap"><table class="data-table"><thead><tr><th>Nama / Username</th><th>Jabatan</th><th>Unit</th><th>Status</th><th>Tindakan</th></tr></thead><tbody>${resp.items.map(u=>`<tr><td class="primary-cell">${esc(u.display_name)}<div class="subtext">${esc(u.username)}</div></td><td>${esc(roles[u.role])}</td><td>${esc(u.unit||'—')}</td><td>${status(u.active?'Aktif':'Tidak Aktif')} ${u.must_change?status('Password Sementara'):''}</td><td><button class="table-action" data-act="reset-user" data-id="${esc(u.id)}">Reset Password</button>${u.id!==currentUser.id?`<button class="table-action" data-act="toggle-user" data-id="${esc(u.id)}">${u.active?'Nonaktifkan':'Aktifkan'}</button>`:''}</td></tr>`).join('')}</tbody></table></div></div>`);
}
function userModal(){
 const options=Object.entries(roles).map(([k,v])=>`<option value="${k}">${esc(v)}</option>`).join('');
 showModal('Buat Akun Staf Baru','Akun individu, bukan username bersama. Password sementara akan otomatis dibuat aman.',
 `<form id="user-form" class="form-stack"><div class="form-grid"><div class="field"><label>Username</label><input name="username" pattern="[A-Za-z0-9._-]{3,40}" required></div><div class="field"><label>Nama lengkap</label><input name="display_name" required></div><div class="field"><label>Role</label><select name="role">${options}</select></div><div class="field"><label>Unit kerja (pilih untuk Operator/Reviewer)</label><select name="unit"><option value="">Unit umum</option><option>WR I</option><option>WR II</option><option>WR III</option></select></div><div class="field full"><label>Email (opsional)</label><input name="email" type="email"></div></div><button class="btn primary" type="submit">Buat Akun & Password Sementara</button></form>`);
 document.getElementById('user-form').addEventListener('submit',async e=>{e.preventDefault();const btn=e.target.querySelector('button');btn.disabled=true;
 try{let d=await api('users',{method:'POST',body:formData(e.target)});closeModal();showSecret(d.username,d.temporary_password);}
 catch(ex){btn.disabled=false;toast(msg(ex),true);}});
}
function showSecret(username,password){
 showModal('Akun Berhasil Dibuat','Password ini tidak dapat dilihat lagi setelah jendela ditutup.',
 `<div class="temp-credential"><div>Username</div><code>${esc(username)}</code><div>Password sementara (satu kali tampil)</div><code id="secret-temp">${esc(password)}</code><button class="btn primary" data-act="copy-secret">${icon('clipboard')} Salin Password</button></div><p class="note-blue">Pengguna wajib login dan langsung mengganti password. Bagikan lewat pesan pribadi yang aman.</p>`,button('close-secret','Selesai','primary'));
}
async function renderAudit(){let x=await api('audit');pageData=x.items;
 shell(`${heading('Jejak Aktivitas & Audit','Mencatat siapa membuat dan mengubah data, kapan, dan jenis tindakannya.')}
 <div class="panel"><div class="table-wrap"><table class="data-table"><thead><tr><th>Tanggal</th><th>Aktor / Role</th><th>Aksi</th><th>Modul</th><th>ID Record</th></tr></thead><tbody>${x.items.map(o=>`<tr><td>${fmt(o.at)}</td><td>${val(o.actor_id)}<div class="subtext">${esc(o.actor_role)}</div></td><td>${esc(o.action)}</td><td>${esc(o.kind)}</td><td>${esc(o.record_id)}</td></tr>`).join('')}</tbody></table>${!x.items.length?`<div class="empty-state"><h3>Belum ada perubahan</h3><p>Audit akan terisi setelah akun, acara, tugas, dan verifikasi digunakan.</p></div>`:''}</div></div>`);
}
async function renderIntegrations(){let x=await api('integrations/status'),g=x.google;
 shell(`${heading('Pengaturan Google & Backup','Monitoring koneksi Google Sheets/Drive, antrean sinkronisasi, dan pilihan backup.')}<div class="status-line ${g.configured?'good':''}">${g.configured?'Konfigurasi service account ditemukan pada server. Jalankan sinkronisasi untuk memeriksa hak akses API.':'Google belum terhubung melalui kredensial backend. Portal tetap bekerja dengan database SQLite lokal sampai Google dikonfigurasi.'}</div>
 <section class="report-grid"><div class="report-card"><h3>Database Utama</h3><div class="kpi-number">SQLite</div><p>Data permanen, audit, transaksi, dan sesi login tersimpan pada volume privat server. Bukan localStorage.</p></div><div class="report-card"><h3>Google Sheets / Drive</h3><div class="kpi-number">${g.configured?'READY':'SETUP'}</div><p>Sheets menjadi salinan operasional; Google Drive menyimpan salinan bukti. Belum otomatis jika service account belum memiliki izin.</p></div></section>
 <div class="panel"><div class="panel-head"><div><h3 class="panel-title">Integrasi Institusi ITB Carnegie</h3><p class="small-text">Akun institusi dan file yang sudah disiapkan di Google Drive.</p></div></div><div class="need-action"><ul class="list-plain">
 <li><strong>Google Sheets 18 tab</strong><a class="link-out" target="_blank" rel="noopener noreferrer" href="https://docs.google.com/spreadsheets/d/152y6XSRb3xN3q0sSSJurTmL7HMM17d2DB1wvnGZcJhk/edit">Buka file</a></li>
 <li><strong>Folder Google Drive CSC-MS</strong><a class="link-out" target="_blank" rel="noopener noreferrer" href="https://drive.google.com/drive/folders/12a2u3C7yRWFweeEuO6kZB2Eaat34C292">Buka folder</a></li>
 <li><strong>Antrean record menunggu sinkronisasi</strong><span class="numeric">${x.pending_sync}</span></li>
 <li><strong>Service Account</strong>${status(g.configured?'Terpasang':'Belum terpasang')}</li>
 </ul><div class="btn-row">${button('sync-google','Sinkronkan 40 Record','primary')}${button('backup-google','Backup Bukti ke Drive')}</div></div></div>
 <div class="report-card"><h3>Konfigurasi Web Editor</h3><p>Pasang Google service-account JSON di luar direktori publik; aktifkan Sheets dan Drive API; beri service account akses editor ke spreadsheet dan folder bukti; atur variabel lingkungan pada server; jalankan tes sinkronisasi. Jangan pernah menaruh private key di HTML/JS ataupun di Google Sheet.</p><p>Untuk backup SQLite, jalankan perintah python manage.py backup. Backup harus disalin ke lokasi aman yang berbeda dari server.</p></div>`);
}
function exportCsv(){
 if(!pageData.length)return toast('Belum ada data untuk diekspor.',true);
 let keys=[...new Set(pageData.flatMap(x=>Object.keys(x)))];
 const safe=x=>{let v=String(x??'');if(/^[=+\-@\t\r]/.test(v))v="'"+v;return '"'+v.replaceAll('"','""')+'"';};
 const csv='\uFEFF'+[keys.join(','),...pageData.map(o=>keys.map(k=>safe(o[k])).join(','))].join('\r\n');
 const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
 const a=document.createElement('a');a.href=url;a.download='CSC-MS_'+page+'_'+new Date().toISOString().slice(0,10)+'.csv';a.click();URL.revokeObjectURL(url);
}
async function changePasswordModal(){
 showModal('Ganti Password Pribadi','Minimal 12 karakter, tiga unsur kombinasi. Session akan dihapus setelah penggantian.',
 `<form id="self-pw-form" class="form-stack"><div class="field"><label>Password saat ini</label><input name="old_password" type="password" required></div><div class="field"><label>Password baru</label><input name="new_password" type="password" minlength="12" required></div><div class="field"><label>Konfirmasi password baru</label><input name="confirm" type="password" minlength="12" required></div><button type="submit" class="btn primary">Simpan Password</button></form>`);
 document.getElementById('self-pw-form').addEventListener('submit',async e=>{e.preventDefault();let d=formData(e.target);if(d.new_password!==d.confirm)return toast('Konfirmasi password tidak cocok.',true);
 try{await api('auth/change-password',{method:'POST',body:{old_password:d.old_password,new_password:d.new_password}});closeModal();currentUser=null;csrf='';renderLogin('Password berhasil diubah. Silakan login ulang.');}catch(ex){toast(msg(ex),true);}});
}
async function renderWeeklyScores(){
 const [scores,students]=await Promise.all([api('records/weekly_score'),api('records/student')]);
 appData.students=students.items;
 pageData=scores.items;
 shell(`${heading('Penilaian Mingguan Kontribusi','Dihasilkan otomatis setiap kali PIC menerima, menolak, atau meminta revisi tugas.')}
 <div class="status-line good">Skor 0–100: kualitas hasil 40%, pencapaian target 25%, ketepatan waktu 15%, inisiatif 10%, kerja sama 10%. Skor ini tidak dapat diubah lewat formulir umum.</div>
 <div class="panel"><div class="table-wrap">${scores.items.length?`<table class="data-table"><thead><tr><th>Tanggal QC</th><th>Mahasiswa</th><th>Tugas</th><th>Nilai</th><th>Keputusan</th><th>Catatan</th></tr></thead><tbody>${scores.items.map(o=>`<tr><td>${fmt(o.reviewed_at)}</td><td>${esc(studentName(o.student_id))}</td><td>${esc(o.task_id)}</td><td><strong>${esc(o.weighted_score)}/100</strong></td><td>${status(o.result_status)}</td><td>${val(o.review_note)}</td></tr>`).join('')}</tbody></table>`:`<div class="empty-state"><h3>Belum ada penilaian mingguan</h3><p>PIC membuka Penugasan → Detail → Bukti & QC. Nilai tersimpan otomatis setelah pemeriksaan bukti.</p></div>`}</div></div>`);
}
async function taiwanDecisionModal(id){const o=pageData.find(x=>x.id===id);if(!o)return;closeModal();
 showModal('Keputusan Rektor Program Taiwan',`Pengajuan ${id} · ${o.partner}`,
 `<div class="form-note">Memenuhi syarat internal tidak menjamin diterima universitas mitra. Jalur referensi harus diverifikasi PMB dan Keuangan. Jalur alternatif harus punya tugas Accepted dengan QC ≥85. Penggunaan referensi ganda wajib disetujui eksplisit.</div>
 <form id="taiwan-decision-form" class="form-stack"><div class="field"><label>Keputusan</label><select name="decision"><option value="yes">Setujui Pemenuhan Syarat Internal</option><option value="no">Tolak</option></select></div><label class="field-checkbox"><input name="allow_dual_use" type="checkbox"> Izinkan satu referensi digunakan kembali untuk fasilitas berbeda (setelah menilai kasus)</label><div class="field"><label>Catatan Rektor</label><textarea name="note" rows="3" required></textarea></div><button type="submit" class="btn primary">Sahkan Keputusan</button></form>`);
 document.querySelector('#taiwan-decision-form').addEventListener('submit',async e=>{e.preventDefault();let d=formData(e.target),b=e.target.querySelector('button');b.disabled=true;
 try{await api(`taiwan/${id}/decision`,{method:'POST',body:{version:o.version,approve:d.decision==='yes',allow_dual_use:d.allow_dual_use==='on',note:d.note}});closeModal();toast('Keputusan program Taiwan disimpan.');await navigate('taiwan');}
 catch(ex){b.disabled=false;toast(msg(ex),true);}});
}
async function onClick(e){let btn=e.target.closest('[data-act],[data-nav]');if(!btn)return;
 if(btn.dataset.nav){await navigate(btn.dataset.nav);return;}
 const action=btn.dataset.act,id=btn.dataset.id;
 try{if(action==='close-modal'){closeModal();return;}
 if(action==='close-secret'){closeModal();await navigate('users');return;}
 if(action==='nav-toggle'){navOpen=!navOpen;document.querySelector('.sidebar')?.classList.toggle('open',navOpen);document.querySelector('.mobile-shade')?.classList.toggle('open',navOpen);return;}
 if(action==='logout'){await api('auth/logout',{method:'POST'});currentUser=null;csrf='';renderLogin();return;}
 if(action==='change-password'){await changePasswordModal();return;}
 if(action==='new-record'){formForNewOrEdit();return;}
 if(action==='edit'){formForNewOrEdit(pageData.find(x=>x.id===id));return;}
 if(action==='view'){await viewRecord(id);return;}
 if(action==='evidence'){await evidenceModal(id);return;}
 if(action==='qc'){await qcModal(id);return;}
 if(action==='verify-pmb'||action==='verify-finance'){await verifyReferral(id,action==='verify-pmb'?'pmb':'finance');return;}
 if(action==='exempt'){await exemptionModal(id);return;}
 if(action==='annual-decision'){await annualDecisionModal(id);return;}
 if(action==='taiwan-decision'){await taiwanDecisionModal(id);return;}
 if(action==='export-csv'){exportCsv();return;}
 if(action==='new-user'){userModal();return;}
 if(action==='copy-secret'){await navigator.clipboard.writeText(document.getElementById('secret-temp')?.textContent||'');toast('Password disalin. Bagikan hanya kepada pemilik akun.');return;}
 if(action==='reset-user'){
   if(!window.confirm('Reset password sementara pengguna ini? Sesi lama akan keluar dan password hanya ditampilkan sekali.'))return;
   let x=await api(`users/${id}/reset-password`,{method:'POST'});
   let item=pageData.find(y=>y.id===id);showSecret(item.username,x.temporary_password);return;
 }
 if(action==='toggle-user'){
   let item=pageData.find(y=>y.id===id);if(!item)return;
   if(!window.confirm(`${item.active?'Nonaktifkan':'Aktifkan'} akun ${item.username}?`))return;
   await api(`users/${id}`,{method:'PATCH',body:{active:!item.active}});toast('Status pengguna diperbarui.');await navigate('users');return;
 }
 if(action==='sync-google'){const x=await api('integrations/sync',{method:'POST'});toast(x.configured?`Sinkron: ${x.synced} berhasil, ${x.failed} gagal.`:'Google belum terhubung. Silakan konfigurasi service account.',!x.configured||x.failed>0);await navigate('integrations');return;}
 if(action==='backup-google'){const x=await api('integrations/upload-backups',{method:'POST'});toast(`${x.backed_up} file dicadangkan, ${x.errors.length} gagal.`,x.errors.length>0);await navigate('integrations');return;}
 }catch(ex){toast(msg(ex),true);}
}
async function onSubmit(e){if(e.target.id==='login-form'){
 e.preventDefault();let d=formData(e.target),b=e.target.querySelector('button');b.disabled=true;
 try{const x=await api('auth/login',{method:'POST',body:d});currentUser=x.user;csrf=x.csrf;if(x.must_change)renderChange();else await navigate('dashboard');}
 catch(ex){renderLogin(msg(ex));}}
 if(e.target.id==='password-form'){
 e.preventDefault();let d=formData(e.target),b=e.target.querySelector('button');if(d.confirm_password!==d.new_password)return renderChange('Konfirmasi password baru tidak cocok.');b.disabled=true;
 try{await api('auth/change-password',{method:'POST',body:{old_password:d.old_password,new_password:d.new_password}});currentUser=null;csrf='';renderLogin('Password berhasil diganti. Silakan login kembali.');}
 catch(ex){renderChange(msg(ex));}}
}
function onSearch(e){if(e.target.id!=='search-filter')return;const term=e.target.value.toLowerCase().trim();document.querySelectorAll('tbody tr[data-query]').forEach(r=>{r.hidden=!!term&&!r.dataset.query.includes(term);});}
document.addEventListener('click',onClick);
document.addEventListener('submit',onSubmit);
document.addEventListener('input',onSearch);
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal();});
bootstrap();
})();
