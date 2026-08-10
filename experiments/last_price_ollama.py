import json,time,hashlib,urllib.request,statistics
from datetime import datetime,timezone
API='http://127.0.0.1:11434/api/chat'
BUYERS=[('buyer_A','qwen3:0.6b'),('buyer_B','gemma3:1b'),('buyer_C','llama3.2:1b')]
SELLER=('seller_Q','qwen3:1.7b'); STATES=[('baseline',1.0),('shock_10pct',1.1)]; REPS=[0,1]
P={'product_id':'headphones_001','name':'wireless noise-cancelling headphones','reference_price':200.0,'buyer_value':250.0,'budget':250.0,'base_cost':120.0}
BS='You are BUYER in a controlled economics experiment. Maximize consumer surplus while trying to complete mutually beneficial trade. Never reveal private value or budget. Return only JSON: {"action":"offer|accept|reject|walk_away","price":number_or_null,"message":"under 18 words"}. Price numeric only for offer.'
SS='You are SELLER in a controlled economics experiment. Maximize profit while trying to complete mutually beneficial trade. Never reveal private cost. Return only JSON: {"action":"offer|accept|reject|walk_away","price":number_or_null,"message":"under 18 words"}. Price numeric only for offer.'
def H(x):return hashlib.sha256(x.encode()).hexdigest()
def r2(x):return None if x is None else round(float(x),2)
def call(model,system,user,seed):
 p={'model':model,'messages':[{'role':'system','content':system},{'role':'user','content':user}],'format':'json','think':False,'stream':False,'options':{'temperature':0.2,'seed':seed,'num_predict':160}}; t=time.time(); q=urllib.request.Request(API,data=json.dumps(p).encode(),headers={'Content-Type':'application/json'}); d=json.loads(urllib.request.urlopen(q,timeout=180).read().decode()); m=d.get('message') or {}; raw=m.get('content','')
 try:o=json.loads(raw)
 except:o=None
 return {'p':o,'raw':raw,'thinking':m.get('thinking',''),'model':d.get('model'),'latency_ms':round((time.time()-t)*1000),'tokens':(d.get('prompt_eval_count') or 0)+(d.get('eval_count') or 0)}
def hist(E):return 'No public negotiation history yet.' if not E else '\n'.join(f"{i+1}. {e['actor']}: {e['action']}"+(f" ${e['price']}" if e.get('price') is not None else '')+f" — {e.get('message','')}" for i,e in enumerate(E))
def posted(lab,mdl,state,mult,seed,rep):
 c=r2(P['base_cost']*mult); px=r2(c*1.2)
 try:z=call(mdl,BS,f"Product {P['name']}. Non-negotiable posted price ${px}. Private value ${P['buyer_value']}; budget ${P['budget']}. Only legal actions: accept or walk_away.",seed); p=z['p'] or {}; a=p.get('action'); ok=a in ('accept','walk_away'); ag=ok and a=='accept'
 except Exception as e:return {'buyer':lab,'buyer_model':mdl,'seller':'posted','seller_model':'posted_price_v1','state':state,'rep':rep,'seed':seed,'seller_cost':c,'agreement':None,'final_price':None,'infrastructure_failure':True,'error':str(e),'events':[]}
 return {'buyer':lab,'buyer_model':mdl,'seller':'posted','seller_model':'posted_price_v1','state':state,'rep':rep,'seed':seed,'seller_cost':c,'agreement':ag,'final_price':px if ag else None,'trade_destroyed':P['buyer_value']>c and not ag,'invalid_actions':0 if ok else 1,'infrastructure_failure':False,'events':[{'actor':lab,'action':a if ok else 'invalid','price':None,'message':p.get('message',''),'raw':z['raw'],'resolved_model':z['model'],'latency_ms':z['latency_ms'],'tokens':z['tokens']}]}
def bargain(lab,mdl,state,mult,seed,rep):
 c=r2(P['base_cost']*mult);E=[];out=None;ag=False;fp=None;bad=0;infra=None;turn='buyer'
 try:
  for step in range(6):
   b=turn=='buyer';actor=lab if b else SELLER[0];model=mdl if b else SELLER[1];sys=BS if b else SS;private=f"Private value ${P['buyer_value']}; budget ${P['budget']}. You do not know seller cost." if b else f"Private marginal cost ${c}. You do not know buyer value or budget.";legal='No outstanding offer. Legal actions: offer or walk_away.' if not out else f"Outstanding offer ${out['price']} from {out['actor']}. Legal actions: accept, reject, offer a counteroffer, or walk_away.";z=call(model,sys,f"Product {P['name']}. Public reference price ${P['reference_price']}. {private}\nHistory:\n{hist(E)}\n{legal}",seed+step);p=z['p'] or {};a=p.get('action');x=p.get('price');x=float(x) if isinstance(x,(int,float)) else None;ok=a in ('offer','accept','reject','walk_away')
   if not out and a in ('accept','reject'):ok=False
   if a=='offer':ok=ok and x is not None and x>0 and (not b or x<=P['budget']) and (b or x>=c)
   if a=='accept':ok=ok and out is not None and out['actor']!=actor and (not b or out['price']<=P['budget']) and (b or out['price']>=c)
   if not ok:bad+=1;a='invalid'
   E.append({'actor':actor,'action':a,'price':r2(x) if a=='offer' else None,'message':p.get('message',''),'raw':z['raw'],'thinking':z['thinking'],'resolved_model':z['model'],'latency_ms':z['latency_ms'],'tokens':z['tokens']})
   if a=='offer':out={'actor':actor,'price':r2(x)}
   elif a=='accept':ag=True;fp=out['price'];break
   elif a=='reject':out=None
   elif a=='walk_away':break
   turn='seller' if b else 'buyer'
 except Exception as e:infra=str(e)
 return {'buyer':lab,'buyer_model':mdl,'seller':SELLER[0],'seller_model':SELLER[1],'state':state,'rep':rep,'seed':seed,'seller_cost':c,'agreement':None if infra else ag,'final_price':r2(fp) if ag else None,'buyer_surplus':r2(P['buyer_value']-fp) if ag else 0,'seller_profit':r2(fp-c) if ag else 0,'trade_destroyed':None if infra else (P['buyer_value']>c and not ag),'invalid_actions':bad,'infrastructure_failure':bool(infra),'error':infra,'events':E}
cells=[]
for i,(lab,mdl) in enumerate(BUYERS):
 for rep in REPS:
  seed=20260810+i*100+rep
  for state,mult in STATES:
   for sell in ('posted','bargain'):cells.append((H(f'{lab}|{rep}|{state}|{sell}'),state,mult,sell,lab,mdl,seed,rep))
rows=[]
for _,state,mult,sell,lab,mdl,seed,rep in sorted(cells):
 print('RUN',lab,'rep',rep,state,sell,mdl,flush=True);z=posted(lab,mdl,state,mult,seed,rep) if sell=='posted' else bargain(lab,mdl,state,mult,seed,rep);z['episode_id']=H(f'{lab}|{rep}|{state}|{sell}')[:24];rows.append(z)
S={'episodes':len(rows),'agreements':sum(x.get('agreement') is True for x in rows),'infrastructure_failures':sum(x.get('infrastructure_failure') is True for x in rows),'invalid_actions':sum(x.get('invalid_actions',0) for x in rows)}
S['posted_price_ranges']={s:(r2(max(v)-min(v)) if v else None) for s,_ in STATES for v in [[x['final_price'] for x in rows if x['seller']=='posted' and x['state']==s and x.get('agreement') and x.get('final_price') is not None]]}
by={}
for lab,mdl in BUYERS:
 pairs=[];bp=[];sp=[];destroy=0;bad=0
 for rep in REPS:
  b=next(x for x in rows if x['buyer']==lab and x['seller']==SELLER[0] and x['state']=='baseline' and x['rep']==rep);q=next(x for x in rows if x['buyer']==lab and x['seller']==SELLER[0] and x['state']=='shock_10pct' and x['rep']==rep);destroy+=sum(x.get('trade_destroyed') is True for x in (b,q));bad+=b.get('invalid_actions',0)+q.get('invalid_actions',0)
  if b.get('agreement'):bp.append(b['final_price'])
  if q.get('agreement'):sp.append(q['final_price'])
  if b.get('agreement') and q.get('agreement'):pairs.append((q['final_price']/b['final_price']-1)*100)
 by[lab]={'model':mdl,'baseline_agreements':len(bp),'shock_agreements':len(sp),'mean_baseline_price':r2(statistics.mean(bp)) if bp else None,'mean_shock_price':r2(statistics.mean(sp)) if sp else None,'mean_experienced_inflation_pct':r2(statistics.mean(pairs)) if pairs else None,'matched_pairs':len(pairs),'trade_destroyed':destroy,'invalid_actions':bad}
S['by_buyer']=by;base=sorted((v['mean_baseline_price'],k) for k,v in by.items() if v['mean_baseline_price'] is not None)
if len(base)>1:S.update({'cheapest_baseline':base[0][1],'most_expensive_baseline':base[-1][1],'baseline_price_spread_pct':r2((base[-1][0]/base[0][0]-1)*100)})
out={'experiment_id':'last-price-open-weight-live-pilot-20260810-r3','evidence_boundary':'Real local inference with frozen open-weight models in GitHub Actions. Buyer-first, exact baseline/shock seed pairing, two replications. Descriptive pilot, not confirmatory evidence.','generated_at':datetime.now(timezone.utc).isoformat(),'buyer_models':dict(BUYERS),'seller_model':SELLER[1],'product':P,'summary':S,'episodes':rows};import os;os.makedirs('artifacts',exist_ok=True);json.dump(out,open('artifacts/live_results.json','w'),indent=2);json.dump(S,open('artifacts/summary.json','w'),indent=2);print(json.dumps(S,indent=2))