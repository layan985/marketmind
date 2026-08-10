import json, os, time, hashlib, urllib.request
from datetime import datetime, timezone

API='http://127.0.0.1:11434/api/chat'
BUYERS=[('buyer_A','qwen3:0.6b'),('buyer_B','gemma3:1b'),('buyer_C','llama3.2:1b')]
SELLER=('seller_Q','qwen3:1.7b')
STATES=[('baseline',1.0),('shock_10pct',1.1)]
P={'product_id':'headphones_001','name':'wireless noise-cancelling headphones','reference_price':200.0,'buyer_value':250.0,'budget':250.0,'base_cost':120.0}
BS='You are BUYER in a controlled economics experiment. Maximize consumer surplus while trying to complete mutually beneficial trade. Never reveal your private value or budget. Return only JSON with keys action, price, message. action is offer, accept, reject, or walk_away. price is numeric only for offer, otherwise null. message under 18 words.'
SS='You are SELLER in a controlled economics experiment. Maximize profit while trying to complete mutually beneficial trade. Never reveal your private cost. Return only JSON with keys action, price, message. action is offer, accept, reject, or walk_away. price is numeric only for offer, otherwise null. message under 18 words.'

def h(x):return hashlib.sha256(x.encode()).hexdigest()
def r2(x):return None if x is None else round(float(x),2)
def call(model,system,user,seed):
    payload={'model':model,'messages':[{'role':'system','content':system},{'role':'user','content':user}],'format':'json','think':False,'stream':False,'options':{'temperature':0.2,'seed':seed,'num_predict':160}}
    started=time.time(); q=urllib.request.Request(API,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(q,timeout=180) as resp:d=json.loads(resp.read().decode())
    msg=d.get('message') or {}; raw=msg.get('content','')
    try:p=json.loads(raw)
    except Exception:p=None
    return {'parsed':p,'raw':raw,'thinking':msg.get('thinking',''),'resolved_model':d.get('model'),'prompt_eval_count':d.get('prompt_eval_count'),'eval_count':d.get('eval_count'),'latency_ms':round((time.time()-started)*1000)}

def hist(events):
    if not events:return 'No public negotiation history yet.'
    return '\n'.join(f"{i+1}. {e['actor']}: {e['action']}"+(f" ${e['price']}" if e.get('price') is not None else '')+f" — {e.get('message','')}" for i,e in enumerate(events))

def posted(label,model,state,mult,seed):
    cost=r2(P['base_cost']*mult); px=r2(cost*1.2)
    try:c=call(model,BS,f"Product: {P['name']}. Non-negotiable posted price ${px}. Private value ${P['buyer_value']}; budget ${P['budget']}. The ONLY legal actions are accept or walk_away. Choose one.",seed); p=c['parsed'] or {}; a=p.get('action'); valid=a in ('accept','walk_away'); agree=valid and a=='accept'
    except Exception as e:return {'buyer':label,'buyer_model':model,'seller':'posted','seller_model':'posted_price_v1','state':state,'seller_cost':cost,'agreement':None,'final_price':None,'infrastructure_failure':True,'error':str(e),'events':[]}
    return {'buyer':label,'buyer_model':model,'seller':'posted','seller_model':'posted_price_v1','state':state,'seller_cost':cost,'agreement':agree,'final_price':px if agree else None,'trade_destroyed':P['buyer_value']>cost and not agree,'invalid_actions':0 if valid else 1,'infrastructure_failure':False,'events':[{'actor':label,'action':a if valid else 'invalid','price':None,'message':p.get('message',''),'raw':c['raw'],'resolved_model':c['resolved_model'],'latency_ms':c['latency_ms'],'tokens':(c.get('prompt_eval_count') or 0)+(c.get('eval_count') or 0)}]}

def bargain(label,model,state,mult,seed):
    cost=r2(P['base_cost']*mult); events=[]; outstanding=None; agree=False; fp=None; bad=0; infra=None; turn='seller'
    try:
      for step in range(6):
        isbuyer=turn=='buyer'; actor=label if isbuyer else SELLER[0]; mdl=model if isbuyer else SELLER[1]; sys=BS if isbuyer else SS
        private=(f"Private value ${P['buyer_value']}; budget ${P['budget']}. You do not know seller cost." if isbuyer else f"Private marginal cost ${cost}. You do not know buyer value or budget.")
        legal=('There is no outstanding offer. Legal actions now: offer or walk_away.' if not outstanding else f"Outstanding offer ${outstanding['price']} from {outstanding['actor']}. Legal actions now: accept, reject, offer a counteroffer, or walk_away.")
        prompt=f"Product: {P['name']}. Public reference price ${P['reference_price']}. {private}\nHistory:\n{hist(events)}\n{legal} Choose next action."
        c=call(mdl,sys,prompt,seed+step); p=c['parsed'] or {}; a=p.get('action'); x=p.get('price'); x=float(x) if isinstance(x,(int,float)) else None; valid=a in ('offer','accept','reject','walk_away')
        if not outstanding and a in ('accept','reject'):valid=False
        if a=='offer':valid=valid and x is not None and x>0 and (not isbuyer or x<=P['budget']) and (isbuyer or x>=cost)
        if a=='accept':valid=valid and outstanding is not None and outstanding['actor']!=actor and (not isbuyer or outstanding['price']<=P['budget']) and (isbuyer or outstanding['price']>=cost)
        if not valid:bad+=1; a='invalid'
        events.append({'actor':actor,'action':a,'price':r2(x) if a=='offer' else None,'message':p.get('message',''),'raw':c['raw'],'thinking':c.get('thinking',''),'resolved_model':c['resolved_model'],'latency_ms':c['latency_ms'],'tokens':(c.get('prompt_eval_count') or 0)+(c.get('eval_count') or 0)})
        if a=='offer':outstanding={'actor':actor,'price':r2(x)}
        elif a=='accept':agree=True; fp=outstanding['price']; break
        elif a=='reject':outstanding=None
        elif a=='walk_away':break
        turn='seller' if isbuyer else 'buyer'
    except Exception as e:infra=str(e)
    return {'buyer':label,'buyer_model':model,'seller':SELLER[0],'seller_model':SELLER[1],'state':state,'seller_cost':cost,'agreement':None if infra else agree,'final_price':r2(fp) if agree else None,'buyer_surplus':r2(P['buyer_value']-fp) if agree else 0,'seller_profit':r2(fp-cost) if agree else 0,'trade_destroyed':None if infra else (P['buyer_value']>cost and not agree),'invalid_actions':bad,'infrastructure_failure':bool(infra),'error':infra,'events':events}

cells=[]
for state,mult in STATES:
  for seller in ('posted','bargain'):
    for i,(lab,mdl) in enumerate(BUYERS):cells.append((h(f'{state}|{seller}|{lab}'),state,mult,seller,lab,mdl,20260810+i*100+(10 if state!='baseline' else 0)))
rows=[]
for _,state,mult,seller,lab,mdl,seed in sorted(cells):
    print('RUN',state,seller,lab,mdl,flush=True); row=posted(lab,mdl,state,mult,seed) if seller=='posted' else bargain(lab,mdl,state,mult,seed); row['episode_id']=h(f'{state}|{seller}|{lab}')[:24]; rows.append(row)
summary={'episodes':len(rows),'agreements':sum(x.get('agreement') is True for x in rows),'infrastructure_failures':sum(x.get('infrastructure_failure') is True for x in rows),'invalid_actions':sum(x.get('invalid_actions',0) for x in rows)}
summary['posted_price_ranges']={s:(r2(max(v)-min(v)) if v else None) for s,_ in STATES for v in [[x['final_price'] for x in rows if x['seller']=='posted' and x['state']==s and x.get('agreement') and x.get('final_price') is not None]]}
by={}
for lab,mdl in BUYERS:
    b=next(x for x in rows if x['buyer']==lab and x['seller']==SELLER[0] and x['state']=='baseline'); q=next(x for x in rows if x['buyer']==lab and x['seller']==SELLER[0] and x['state']=='shock_10pct')
    by[lab]={'model':mdl,'baseline_agreement':b.get('agreement'),'baseline_price':b.get('final_price'),'shock_agreement':q.get('agreement'),'shock_price':q.get('final_price'),'experienced_inflation_pct':r2((q['final_price']/b['final_price']-1)*100) if b.get('agreement') and q.get('agreement') else None,'trade_destroyed':sum(x.get('trade_destroyed') is True for x in (b,q)),'invalid_actions':b.get('invalid_actions',0)+q.get('invalid_actions',0)}
summary['by_buyer']=by
bp=sorted((v['baseline_price'],k) for k,v in by.items() if v['baseline_price'] is not None)
if len(bp)>1:summary.update({'cheapest_baseline':bp[0][1],'most_expensive_baseline':bp[-1][1],'baseline_price_spread_pct':r2((bp[-1][0]/bp[0][0]-1)*100)})
out={'experiment_id':'last-price-open-weight-live-pilot-20260810-r2','evidence_boundary':'Real local inference with frozen open-weight models in GitHub Actions. Small descriptive pilot, not the 72,000-episode confirmatory benchmark.','generated_at':datetime.now(timezone.utc).isoformat(),'buyer_models':dict(BUYERS),'seller_model':SELLER[1],'product':P,'summary':summary,'episodes':rows}
os.makedirs('artifacts',exist_ok=True);json.dump(out,open('artifacts/live_results.json','w'),indent=2);json.dump(summary,open('artifacts/summary.json','w'),indent=2);print(json.dumps(summary,indent=2))