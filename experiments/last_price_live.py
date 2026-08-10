import os,json,time,hashlib,urllib.request,urllib.error
from datetime import datetime,timezone
T=os.environ['GITHUB_TOKEN']; BASE='https://models.github.ai'; H={'Authorization':f'Bearer {T}','Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2026-03-10','Content-Type':'application/json'}
def req(path,data=None,retries=4):
 b=None if data is None else json.dumps(data).encode()
 for i in range(retries):
  try:
   q=urllib.request.Request(BASE+path,data=b,headers=H,method='POST' if b else 'GET')
   with urllib.request.urlopen(q,timeout=120) as r:return json.loads(r.read().decode())
  except urllib.error.HTTPError as e:
   x=e.read().decode(errors='replace')
   if e.code in (429,500,502,503,504) and i<retries-1:time.sleep(3*(2**i));continue
   raise RuntimeError(f'HTTP {e.code}: {x[:800]}')

def sh(x):return hashlib.sha256(x.encode()).hexdigest()
def r2(x):return None if x is None else round(float(x),2)
def parse(s):
 if not s:return None
 s=s.strip().replace('```json','').replace('```','').strip()
 try:return json.loads(s)
 except:pass
 a,b=s.find('{'),s.rfind('}')
 try:return json.loads(s[a:b+1]) if a>=0 and b>a else None
 except:return None
C=req('/catalog/models'); ids=[m['id'] for m in C]
prefs=[['openai/gpt-4.1-mini','openai/gpt-4o-mini'],['openai/gpt-4.1','openai/gpt-4o'],['deepseek/DeepSeek-V3-0324','deepseek/DeepSeek-V3','deepseek/DeepSeek-R1'],['meta/Llama-4-Scout-17B-16E-Instruct','meta/Llama-3.3-70B-Instruct','meta/Meta-Llama-3.1-70B-Instruct'],['microsoft/Phi-4','microsoft/Phi-4-mini-instruct'],['mistral-ai/Mistral-Large-2411','mistral-ai/Mistral-Small-2503']]
M=[]
for g in prefs:
 h=next((x for x in g if x in ids),None)
 if h and h not in M:M.append(h)
if len(M)<4:
 for m in C:
  x=m['id']; out=m.get('supported_output_modalities') or []
  if x not in M and not any(k in x.lower() for k in ('embed','image','audio')) and (not out or 'text' in out):M.append(x)
  if len(M)>=4:break
M=M[:4]
if len(M)<2:raise RuntimeError('Not enough text models in catalog')
SELL='openai/gpt-4.1-mini' if 'openai/gpt-4.1-mini' in ids else M[0]
print('BUYERS',M);print('SELLER',SELL)
P={'name':'wireless noise-cancelling headphones','reference':200.0,'value':250.0,'budget':250.0,'cost':120.0}; STATES=[('baseline',1.0),('shock_10pct',1.10)]
BS='You are BUYER in a controlled economics experiment. Maximize consumer surplus while completing mutually beneficial trade. Never reveal private value or budget. Output one JSON object only: {"action":"offer|accept|reject|walk_away","price":number_or_null,"message":"under 20 words"}. Price numeric only for offer.'
SS='You are SELLER in a controlled economics experiment. Maximize profit while completing mutually beneficial trade. Never reveal private cost. Output one JSON object only: {"action":"offer|accept|reject|walk_away","price":number_or_null,"message":"under 20 words"}. Price numeric only for offer.'
def call(model,system,user,seed):
 d=req('/inference/chat/completions',{'model':model,'messages':[{'role':'system','content':system},{'role':'user','content':user}],'temperature':0.2,'max_tokens':180,'seed':seed,'response_format':{'type':'json_object'},'stream':False}); raw=d.get('choices',[{}])[0].get('message',{}).get('content','');return {'p':parse(raw),'raw':raw,'model':d.get('model',model),'usage':d.get('usage')}
def hist(E):return 'No history.' if not E else '\n'.join(f"{i+1}. {e['actor']} {e['action']}"+(f" ${e['price']}" if e.get('price') is not None else '') for i,e in enumerate(E))
def posted(lab,mdl,state,mult,seed):
 c=r2(P['cost']*mult); px=r2(c*1.2)
 try:q=call(mdl,BS,f"Product {P['name']}. Non-negotiable posted price ${px}. Private value ${P['value']}; budget ${P['budget']}. Choose accept or walk_away only.",seed);p=q['p'] or {};a=p.get('action');ok=a in ('accept','walk_away');ag=ok and a=='accept';err=None
 except Exception as e:return {'buyer':lab,'buyer_model':mdl,'seller':'posted','seller_model':'posted_price_v1','state':state,'cost':c,'agreement':None,'final_price':None,'infrastructure_failure':True,'error':str(e),'events':[]}
 return {'buyer':lab,'buyer_model':mdl,'seller':'posted','seller_model':'posted_price_v1','state':state,'cost':c,'agreement':ag,'final_price':px if ag else None,'buyer_surplus':r2(P['value']-px) if ag else 0,'seller_profit':r2(px-c) if ag else 0,'trade_destroyed':P['value']>c and not ag,'invalid_actions':0 if ok else 1,'infrastructure_failure':False,'events':[{'actor':lab,'action':a if ok else 'invalid','price':None,'raw':q['raw'],'resolved_model':q['model'],'usage':q['usage']}]}
def bargain(lab,mdl,state,mult,seed):
 c=r2(P['cost']*mult);E=[];o=None;ag=False;fp=None;bad=0;infra=None;turn='seller'
 try:
  for step in range(4):
   b=turn=='buyer'; actor=lab if b else 'seller_Q'; model=mdl if b else SELL; sys=BS if b else SS; priv=f"Private value ${P['value']}; budget ${P['budget']}. You do not know seller cost." if b else f"Private marginal cost ${c}. You do not know buyer value or budget."
   q=call(model,sys,f"Product {P['name']}. Public reference ${P['reference']}. {priv}\nHistory:\n{hist(E)}\n"+(f"Outstanding offer ${o['price']} from {o['actor']}." if o else 'No outstanding offer.')+' Choose next action.',seed+step);p=q['p'] or {};a=p.get('action');x=p.get('price');x=float(x) if isinstance(x,(int,float)) else None;ok=a in ('offer','accept','reject','walk_away')
   if a=='offer':ok=ok and x is not None and x>0 and (not b or x<=P['budget']) and (b or x>=c)
   if a=='accept':ok=ok and o is not None and o['actor']!=actor and (not b or o['price']<=P['budget']) and (b or o['price']>=c)
   if not ok:bad+=1;a='invalid'
   E.append({'actor':actor,'action':a,'price':r2(x) if a=='offer' else None,'raw':q['raw'],'resolved_model':q['model'],'usage':q['usage']})
   if a=='offer':o={'actor':actor,'price':r2(x)}
   elif a=='accept':ag=True;fp=o['price'];break
   elif a=='reject':o=None
   elif a=='walk_away':break
   turn='seller' if b else 'buyer'
 except Exception as e:infra=str(e)
 return {'buyer':lab,'buyer_model':mdl,'seller':'seller_Q','seller_model':SELL,'state':state,'cost':c,'agreement':None if infra else ag,'final_price':r2(fp) if ag else None,'buyer_surplus':r2(P['value']-fp) if ag else 0,'seller_profit':r2(fp-c) if ag else 0,'trade_destroyed':None if infra else (P['value']>c and not ag),'invalid_actions':bad,'infrastructure_failure':bool(infra),'error':infra,'events':E}
L=[f'buyer_{chr(65+i)}' for i in range(len(M))]; cells=[]
for s,mul in STATES:
 for sell in ('posted','seller_Q'):
  for i,(lab,mdl) in enumerate(zip(L,M)):cells.append((sh(f'{s}|{sell}|{lab}'),s,mul,sell,lab,mdl,20260810+i*100+(10 if s!='baseline' else 0)))
R=[]
for _,s,mul,sell,lab,mdl,seed in sorted(cells):
 print('RUN',s,sell,lab,mdl,flush=True);z=posted(lab,mdl,s,mul,seed) if sell=='posted' else bargain(lab,mdl,s,mul,seed);z['episode_id']=sh(f'{s}|{sell}|{lab}')[:24];R.append(z)
A={'episodes':len(R),'infrastructure_failures':sum(bool(x.get('infrastructure_failure')) for x in R),'agreements':sum(x.get('agreement') is True for x in R)}
A['posted_price_ranges']={s:(r2(max(v)-min(v)) if v else None) for s,_ in STATES for v in [[x['final_price'] for x in R if x['seller']=='posted' and x['state']==s and x.get('agreement') and x.get('final_price') is not None]]}
B={}
for lab,mdl in zip(L,M):
 b=next((x for x in R if x['buyer']==lab and x['seller']=='seller_Q' and x['state']=='baseline'),None);q=next((x for x in R if x['buyer']==lab and x['seller']=='seller_Q' and x['state']=='shock_10pct'),None)
 B[lab]={'model':mdl,'baseline_agreement':b.get('agreement') if b else None,'baseline_price':b.get('final_price') if b else None,'shock_agreement':q.get('agreement') if q else None,'shock_price':q.get('final_price') if q else None,'experienced_inflation_pct':r2((q['final_price']/b['final_price']-1)*100) if b and q and b.get('agreement') and q.get('agreement') else None,'trade_destroyed':sum(x.get('trade_destroyed') is True for x in (b,q) if x),'invalid_actions':sum((x.get('invalid_actions') or 0) for x in (b,q) if x)}
A['by_buyer']=B;base=sorted((v['baseline_price'],k) for k,v in B.items() if v['baseline_price'] is not None)
if len(base)>1:A.update({'cheapest_baseline':base[0][1],'most_expensive_baseline':base[-1][1],'baseline_price_spread_pct':r2((base[-1][0]/base[0][0]-1)*100)})
out={'experiment_id':'last-price-github-models-live-pilot-20260810','evidence_boundary':'Real model calls through GitHub Models. Small descriptive pilot; not preregistered confirmatory evidence.','generated_at':datetime.now(timezone.utc).isoformat(),'catalog_count':len(ids),'buyer_models':dict(zip(L,M)),'seller_model':SELL,'product':P,'analysis':A,'episodes':R}
os.makedirs('artifacts',exist_ok=True);json.dump(out,open('artifacts/live_results.json','w'),indent=2);json.dump(A,open('artifacts/summary.json','w'),indent=2);print(json.dumps(A,indent=2))