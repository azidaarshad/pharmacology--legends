from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json, threading, random, time, os, urllib.parse, socket, csv, io, sqlite3
import qrcode

HOST='0.0.0.0'; PORT=int(os.environ.get('PORT','8000'))
PUBLIC=os.path.join(os.path.dirname(__file__),'public')
lock=threading.RLock()
DB_PATH=os.environ.get('DB_PATH', os.path.join('/var/data','pharma_legends.db'))
os.makedirs(os.path.dirname(DB_PATH) or '.', exist_ok=True)

def db_init():
    con=sqlite3.connect(DB_PATH)
    con.execute('CREATE TABLE IF NOT EXISTS app_state (id INTEGER PRIMARY KEY CHECK(id=1), data TEXT NOT NULL, updated_at REAL NOT NULL)')
    con.commit(); con.close()

def db_load():
    con=sqlite3.connect(DB_PATH)
    row=con.execute('SELECT data FROM app_state WHERE id=1').fetchone()
    con.close()
    if not row: return None
    try: return json.loads(row[0])
    except Exception: return None

def db_save(st):
    data=json.dumps(st, ensure_ascii=False, separators=(',',':'))
    con=sqlite3.connect(DB_PATH, timeout=10)
    con.execute('INSERT INTO app_state(id,data,updated_at) VALUES(1,?,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data, updated_at=excluded.updated_at', (data,time.time()))
    con.commit(); con.close()

TEAM_CODES=list('ABCDEF')
TEAM_COLORS=['#ef4444','#3b82f6','#22c55e','#a855f7','#f97316','#eab308']

def make_teams():
    return {c:{'name':f'TEAM {c}','color':col,'hp':1000,'xp':0,'coins':0,'players':[]}
            for c,col in zip(TEAM_CODES,TEAM_COLORS)}

# 2.1 and 2.2 are taken directly from the uploaded learning notes.
topics=[
 ('2.0','Pharmacology Launch','Drug fundamentals: prepare for the pharmacology journey.'),
 ('2.1','Introduction to Pharmacology','Definitions, pharmacodynamics, pharmacokinetics, pharmacotherapeutics, toxicology and medication abbreviations.'),
 ('2.2','Sources of Drugs & Drug Uses','Natural and synthetic sources of drugs, and treatment, prevention, diagnostic, curative, health maintenance, contraceptive and replacement uses.'),
 ('2.3','Types of Drug Preparations','Solid, liquid, topical, implants and parenteral preparations.'),
 ('2.4','Mechanism of Drug Action / Pharmacokinetics','Absorption, distribution, metabolism, excretion, first-pass, onset, peak and duration.'),
 ('2.5','Effects of Drugs','Therapeutic, side, adverse, toxicity, allergy, tolerance, agonist and antagonist effects.'),
 ('2.6','Factors Affecting Medication Action','Age, weight, sex, psychological, physiological/pathological, interactions, timing and storage.'),
 ('2.7','Broad Classification of Drugs','Antimicrobial, pain/inflammation, GI, CNS, respiratory, cardiovascular and nutrition.'),
 ('2.8','Dangerous Drug Act / Poison Ordinance','Controlled drugs, storage, records, administration and stock control.'),
 ('2.9','Legal & Ethical Aspects','Malpractice, medication errors and ethical principles in medication administration.'),
 ('2.10','Principles of Medication Administration','7R and 10R, preparation, checks, refusal, documentation, assessment, evaluation and education.'),
 ('2.11.1','Administration of Oral Medication','Oral medication preparation and administration safety.'),
 ('2.11.2','Parenteral ID / SC / IM / IV','Choose route, site/area, target tissue and technique.'),
 ('2.11.3','Topical & Other Routes','Skin, eye, ear, nasal, inhalation, SL, buccal, pessary, suppository and enema.'),
 ('2.11.4','Documenting Medication Administration','Accurate, complete, timely and objective documentation.'),
 ('2.11.5','Patient Education','Medication instructions, adherence, storage, safety and follow-up.'),
 ('3.0','Traditional & Complementary Medicine','Seven recognised fields, complementary vs alternative and ethical practice.'),
]

Q={
'2.0':[],
'2.1':[
 ('What is pharmacology?','The study/science of drugs, including their actions, uses and effects on the body.'),
 ('Pharmacodynamics asks: what does the drug do to the body, or what does the body do to the drug?','What the drug does to the body.'),
 ('Name the four processes of pharmacokinetics.','Absorption, distribution, metabolism and excretion.'),
 ('What does toxicology study?','Poisons and unwanted effects caused by drugs and other chemicals.')],
'2.2':[
 ('Name TWO natural sources of drugs.','Plant, animal, mineral, microorganism or human.'),
 ('Penicillin is listed in the notes as coming from which microorganism?','Penicillium chrysogenum.'),
 ('Which drug use is represented by vaccination to prevent infectious disease?','Prevention.'),
 ('Antibiotics are an example of which drug use?','Curative treatment.')],
'2.3':[
 ('A gelatin shell containing powder, liquid or oil is a…?','Capsule.'),
 ('Which preparation is inserted into the vagina?','Pessary.'),
 ('A suppository is solid at room temperature and does what at body temperature?','Melts/dissolves.'),
 ('Give one example of a liquid preparation.','Syrup, elixir, linctus, emulsion or mixture.')],
'2.4':[
 ('Name the four main pharmacokinetic processes.','Absorption, distribution, metabolism and excretion.'),
 ('Why can sublingual administration bypass first-pass metabolism?','It is absorbed through highly vascularised oral tissue and bypasses the GI/portal route.'),
 ('Which organs/tissues with high blood perfusion receive drug distribution faster?','Examples in the notes: heart, kidney, liver and brain.'),
 ('What is the active fraction of a protein-bound drug?','The free/unbound drug.')],
'2.5':[
 ('What is a therapeutic effect?','The desired/intended effect of a drug.'),
 ('What is an adverse effect?','An undesired medical problem resulting from taking a medication correctly.'),
 ('What is tolerance?','A reduced response requiring consideration of a higher/repeated dose over time.'),
 ('Naloxone is given as an antagonist to which opioid example in the notes?','Morphine.')],
'2.6':[
 ('Give TWO internal factors affecting drug action.','Age, weight, sex, psychological, physiological/pathological or genetic factors.'),
 ('Why can liver/kidney impairment increase toxicity?','Reduced metabolism or excretion can cause drug accumulation.'),
 ('What is an example of a drug-food interaction in the notes?','Grapefruit or vitamin-K-rich vegetables with warfarin.'),
 ('Why should slow-release or enteric-coated tablets not be crushed unless directed?','Their physical form should not be altered unless instructed.')],
'2.7':[
 ('Do antibiotics treat viral infections?','No.'),
 ('Bactericidal vs bacteriostatic?','Bactericidal kills bacteria; bacteriostatic stops bacterial reproduction.'),
 ('Name TWO broad cardiovascular drug groups listed.','Examples: vasodilators, drugs affecting clotting, diuretics, antihypertensives.'),
 ('What should be monitored before giving digoxin according to the note?','Apex beat; do not give if below 60 beats/min.')],
'2.8':[
 ('Where should dangerous drugs be kept?','In a secure locked/double-lock compartment with controlled key access.'),
 ('Name one DDA drug listed in the notes.','Morphine, pethidine, midazolam/Dormicum, diazepam/Valium or phenobarbitone.'),
 ('When should DDA administration be recorded?','Immediately in the required records such as DDA book/BHT/medication chart.'),
 ('Give ONE detail required in the DDA record.','Patient name/ID, date, drug, dose, time, signatures or stock balance.')],
'2.9':[
 ('Which ethical principle supports a competent patient’s right to make a decision/refuse?','Autonomy.'),
 ('Name the four key malpractice elements.','Duty, breach, causal connection and damage.'),
 ('What is a medication error?','A preventable event that may lead to inappropriate medication use or harm.'),
 ('What is a near miss?','A medication error intercepted before it reaches the patient.')],
'2.10':[
 ('List the first 7R principles.','Right Patient, Medication, Dose, Route, Time, To Refuse, Documentation.'),
 ('What are R8–R10?','Right Assessment, Right Evaluation, Right Client Education.'),
 ('When should documentation be signed?','After administration and after ensuring the oral medication has been taken/seen swallowed.'),
 ('Name THREE checks for the right drug.','When removing from storage, during preparation and before administration.')],
'2.11.1':[
 ('What should the medication preparation area be like?','Clean, bright/well lit and away from distractions.'),
 ('How many label checks are described before administration?','Three.'),
 ('Why should medication prepared by another staff member generally be avoided?','To ensure the person administering has verified/prepared the medication safely.')],
'2.11.2':[
 ('ROUTE MISSION: Mantoux test → choose route.','Intradermal (ID).'),
 ('SITE/TISSUE MISSION: ID injection targets which tissue?','Dermis.'),
 ('ROUTE MISSION: Insulin injection → choose route.','Subcutaneous (SC).'),
 ('TECHNIQUE MISSION: IM injection angle in the supplied note?','90°.'),
 ('CLINICAL MISSION: IM injection — name the target tissue.','Muscle.'),
 ('SAFETY MISSION: If blood appears during the aspiration step described in the note, what is the action?','Stop, remove the needle and prepare new medication.')],
'2.11.3':[
 ('Which route places medicine under the tongue?','Sublingual.'),
 ('Eye drops should be placed where according to the note?','Conjunctiva, not the cornea.'),
 ('For adult ear instillation, how is the ear canal straightened?','Pull the ear up and back.'),
 ('Pessary is inserted into which body site?','Vagina, towards the posterior fornix.'),
 ('What position is used for rectal suppository/enema in the note?','Left lateral.')],
'2.11.4':[
 ('Name FOUR basic documentation items.','Date, time, signature and name.'),
 ('Give TWO documentation principles.','Accurate, complete, timely, objective, and follow hospital policy.'),
 ('If a medication is not given because the patient vomited, what must be recorded?','The reason it was not given and appropriate notification/action.'),
 ('Name THREE effects that may need documentation.','Therapeutic effect, side effect and adverse effect.')],
'2.11.5':[
 ('Name FOUR things the patient should be taught about a medication.','Name, purpose/action, dose, side effects and/or how/when/frequency/duration.'),
 ('What should the patient do with expired medication according to the notes?','Return it to a government pharmacy.'),
 ('What storage advice is given for insulin?','Store in the refrigerator.'),
 ('Should patients share prescribed medicines with family members?','No.')],
'3.0':[
 ('How many T&CM fields are recognised in the supplied notes?','Seven.'),
 ('Name FOUR recognised T&CM fields.','Malay, Chinese, Indian, Homeopathy, Chiropractic, Osteopathy, Islamic Medical Practice.'),
 ('Complementary vs alternative?','Complementary is used alongside conventional medicine; alternative replaces conventional medicine.'),
 ('When should a T&CM practitioner refer a serious/unidentified case?','To a registered medical practitioner/hospital when beyond scope or serious/unidentified.')]
}
BOSS=[
 ('FINAL BOSS 1 — A patient needs insulin. Choose the route and target tissue.','Subcutaneous (SC) into subcutaneous/fatty tissue.'),
 ('FINAL BOSS 2 — A patient is prescribed digoxin and apex beat is 54/min. What should you do based on the note?','Do not give digoxin and report/act according to the note.'),
 ('FINAL BOSS 3 — Patient refuses medication. Name the key right and TWO actions.','Right to Refuse; explain importance/risks, notify prescriber/doctor and document refusal.'),
 ('FINAL BOSS 4 — Medication given correctly but patient develops an undesired medical problem. What effect is this?','Adverse effect.'),
 ('FINAL BOSS 5 — Your team must document a medication after administration. Give the minimum core entries.','Date, time, signature and name; document relevant effects as required.'),
]

db_init()
_loaded=db_load()
state=_loaded or {'room':'PHARMA60','started':False,'phase':'lobby','topic_index':0,'question_index':0,
       'mode':'ALL PLAYERS','timer_end':0,'teams':make_teams(),'players':{},'answers':{},'history':[],'last_event':'Room ready','boss_question_index':0}
state.setdefault('teams', make_teams()); state.setdefault('players', {}); state.setdefault('answers', {}); state.setdefault('history', [])
state.setdefault('boss_question_index', 0); state.setdefault('timer_end', 0); state.setdefault('phase', 'lobby')

def snapshot():
    with lock: return json.loads(json.dumps(state))

def local_ip():
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); ip=s.getsockname()[0]; s.close(); return ip
    except Exception: return 'YOUR-LAPTOP-IP'

def send(h,obj,code=200):
    data=json.dumps(obj).encode(); h.send_response(code); h.send_header('Content-Type','application/json; charset=utf-8'); h.send_header('Cache-Control','no-store'); h.send_header('Content-Length',str(len(data))); h.end_headers(); h.wfile.write(data)

def question_level(code, idx):
    # Difficulty is progressive within each topic; topic 2.11.2 gets extra challenge.
    total=len(Q.get(code,[]))
    if total <= 1: return 'Sederhana'
    if code=='2.11.2' and idx >= 3: return 'Susah'
    if idx >= max(2, total-2): return 'Susah'
    return 'Sederhana'

def question_points(code, idx):
    return 100 if question_level(code, idx)=='Susah' else 50

def current_question():
    if state['phase']=='boss':
        q=BOSS[state['boss_question_index']%len(BOSS)]; return ('FINAL BOSS', 'Final Boss', q[0], q[1], state['boss_question_index']+1, len(BOSS), 'Final Boss', 150)
    code,title,_=topics[state['topic_index']]; qs=Q.get(code,[])
    if not qs:
        return (code,title,'BRIEFING / UNLOCK','Selesaikan briefing untuk membuka topik 2.1.',1,0,'Briefing',0)
    idx=state['question_index']%len(qs); q=qs[idx]
    return (code,title,q[0],q[1],idx+1,len(qs),question_level(code,idx),question_points(code,idx))

class H(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def do_GET(self):
        p=urllib.parse.urlparse(self.path)
        if p.path=='/api/state': return send(self,snapshot())
        if p.path=='/api/info':
            host=self.headers.get('Host','').strip()
            proto=self.headers.get('X-Forwarded-Proto','http').split(',')[0].strip() or 'http'
            if host and not host.startswith('127.0.0.1') and not host.startswith('localhost'):
                join_url=f'{proto}://{host}'
            else:
                join_url=f'http://{local_ip()}:{PORT}'
            return send(self,{'ip':local_ip(),'port':PORT,'join_url':join_url,'public':host not in ('','localhost',f'localhost:{PORT}','127.0.0.1',f'127.0.0.1:{PORT}')})
        if p.path=='/api/qr.png':
            host=self.headers.get('Host','').strip(); proto=self.headers.get('X-Forwarded-Proto','http').split(',')[0].strip() or 'http'
            join_url=f'{proto}://{host}' if host and not host.startswith('127.0.0.1') and not host.startswith('localhost') else f'http://{local_ip()}:{PORT}'
            img=qrcode.make(join_url); buf=io.BytesIO(); img.save(buf,format='PNG'); data=buf.getvalue()
            self.send_response(200); self.send_header('Content-Type','image/png'); self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data); return
        if p.path=='/api/report.csv':
            output=io.StringIO(); w=csv.writer(output); w.writerow(['Question','Topic','Level','Student','Team','Correct','Points','Timestamp'])
            with lock:
                for rec in state.get('history',[]): w.writerow([rec['question'],rec['topic'],rec['level'],rec['student'],rec['team'],rec['correct'],rec['points'],time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(rec['timestamp']))])
            data=output.getvalue().encode('utf-8-sig'); self.send_response(200); self.send_header('Content-Type','text/csv; charset=utf-8'); self.send_header('Content-Disposition','attachment; filename=pharmacology_legends_report.csv'); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data); return
        if p.path=='/api/question':
            with lock:
                code,title,q,a,num,total,level,points=current_question(); return send(self,{'topic_code':code,'topic':title,'question':q,'answer':a,'question_number':num,'total_questions':total,'level':level,'points':points,'answers_count':len(state['answers'])})
        path=p.path
        if path=='/': path='/index.html'
        fn=os.path.join(PUBLIC,path.lstrip('/'))
        if os.path.isfile(fn):
            data=open(fn,'rb').read(); self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data); return
        return send(self,{'error':'not found'},404)
    def do_POST(self):
        try: n=int(self.headers.get('Content-Length','0')); body=json.loads(self.rfile.read(n) or '{}')
        except: body={}
        path=urllib.parse.urlparse(self.path).path
        with lock:
            if path=='/api/join':
                name=str(body.get('name','Player')).strip()[:30] or 'Player'; team=str(body.get('team','A')); pid=str(body.get('player_id') or random.randint(100000,999999))
                if team not in TEAM_CODES: team='A'
                if pid not in state['players'] and len(state['teams'][team]['players'])>=10: return send(self,{'error':f'Team {team} sudah penuh (10 orang).'},409)
                old=state['players'].get(pid)
                if old and old['team']!=team and pid in state['teams'][old['team']]['players']: state['teams'][old['team']]['players'].remove(pid)
                state['players'][pid]={'name':name,'team':team,'joined':time.time()}
                if pid not in state['teams'][team]['players']: state['teams'][team]['players'].append(pid)
                state['last_event']=f'{name} masuk Team {team}'
                db_save(state)
                return send(self,{'player_id':pid,'state':snapshot()})
            if path=='/api/start':
                state.update({'started':True,'phase':'topic','topic_index':0,'question_index':0,'boss_question_index':0,'answers':{},'last_event':'BATTLE STARTED — 2.0','timer_end':0}); db_save(state); return send(self,snapshot())
            if path=='/api/next_question':
                if state['phase']=='boss':
                    if state['boss_question_index']<len(BOSS)-1: state['boss_question_index']+=1; state['answers']={}; state['last_event']='Next Final Boss challenge'
                    else: state['phase']='complete'; state['last_event']='PHARMACOLOGY LEGEND COMPLETED!'
                else:
                    code=topics[state['topic_index']][0]; total=len(Q.get(code,[]))
                    if state['question_index']<total-1: state['question_index']+=1; state['answers']={}; state['last_event']=f'Next challenge — {code}'
                    else: state['last_event']='Topic complete — Game Master boleh NEXT TOPIC'
                db_save(state)
                return send(self,snapshot())
            if path=='/api/next_topic':
                if state['phase']=='complete': return send(self,snapshot())
                if state['phase']=='boss': return send(self,snapshot())
                code=topics[state['topic_index']][0]; total=len(Q.get(code,[]))
                if total>0 and state['question_index']<total-1: return send(self,{'error':'Selesaikan semua soalan topik ini dahulu.'},409)
                if state['topic_index']<len(topics)-1:
                    state['topic_index']+=1; state['question_index']=0; state['answers']={}; state['phase']='topic'; state['last_event']=f'UNLOCKED {topics[state["topic_index"]][0]} — {topics[state["topic_index"]][1]}'
                else:
                    state['phase']='boss'; state['boss_question_index']=0; state['answers']={}; state['last_event']='FINAL BOSS UNLOCKED!'
                db_save(state)
                return send(self,snapshot())
            if path=='/api/set_timer':
                sec=max(0,min(600,int(body.get('seconds',60)))); state['timer_end']=time.time()+sec if sec else 0; state['last_event']=f'Timer {sec}s'; db_save(state); return send(self,snapshot())
            if path=='/api/answer':
                pid=str(body.get('player_id','')); correct=bool(body.get('correct')); pl=state['players'].get(pid)
                if not pl: return send(self,{'error':'Player belum join.'},400)
                if pid in state['answers']: return send(self,{'error':'Anda sudah menjawab soalan ini.'},409)
                team=pl['team']; state['answers'][pid]=correct
                code,title,q,a,num,total,level,points=current_question()
                awarded=points if correct else 0
                if state['phase']=='boss':
                    if correct: state['teams'][team]['xp']+=points; state['teams'][team]['coins']+=50; state['last_event']=f'{pl["name"]}: BOSS HIT! Team {team} +{points} XP'
                    else: state['teams'][team]['hp']=max(0,state['teams'][team]['hp']-50); state['last_event']=f'{pl["name"]}: Boss counter! Team {team} -50 HP'
                else:
                    if correct: state['teams'][team]['xp']+=points; state['teams'][team]['coins']+=20; state['last_event']=f'{pl["name"]}: correct — Team {team} +{points} XP'
                    else: state['teams'][team]['hp']=max(0,state['teams'][team]['hp']-30); state['last_event']=f'{pl["name"]}: wrong — Team {team} -30 HP'
                state['history'].append({'question':q,'topic':title,'level':level,'student':pl['name'],'team':team,'correct':correct,'points':awarded,'timestamp':time.time()})
                db_save(state)
                return send(self,snapshot())
            if path=='/api/attack':
                pid=str(body.get('player_id','')); target=str(body.get('target','')); pl=state['players'].get(pid)
                if not pl or target not in TEAM_CODES or target==pl['team']: return send(self,{'error':'Target tidak sah.'},400)
                attacker=pl['team']
                if state['teams'][attacker]['xp']<50: return send(self,{'error':'Perlu 50 XP untuk menyerang.'},409)
                state['teams'][attacker]['xp']-=50; state['teams'][target]['hp']=max(0,state['teams'][target]['hp']-100); state['last_event']=f'Team {attacker} ATTACK Team {target} — -100 HP'; db_save(state); return send(self,snapshot())
            if path=='/api/reset':
                state.clear(); state.update({'room':'PHARMA60','started':False,'phase':'lobby','topic_index':0,'question_index':0,'mode':'ALL PLAYERS','timer_end':0,'teams':make_teams(),'players':{},'answers':{},'history':[],'last_event':'Room reset','boss_question_index':0}); db_save(state); return send(self,snapshot())
        return send(self,{'error':'bad request'},400)

print(f'Pharmacology Legends Live Classroom — http://localhost:{PORT}')
print(f'Network URL — http://{local_ip()}:{PORT}')
ThreadingHTTPServer((HOST,PORT),H).serve_forever()
