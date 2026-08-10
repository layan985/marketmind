import glob, json, random, statistics
from collections import defaultdict
from pathlib import Path
from scipy.stats import wilcoxon

BUYERS=("qwen17","gemma4","llama3"); EXPECTED=702

def avg(x): return statistics.fmean(x) if x else None
def wp(x):
    if not x: return None
    if all(abs(v)<1e-12 for v in x): return 1.0
    return float(wilcoxon(x,zero_method="wilcox",alternative="two-sided",method="auto").pvalue)
def ci(x,n=5000):
    if not x:return [None,None]
    if len(x)==1:return [x[0],x[0]]
    rng=random.Random(20260810); b=[statistics.fmean(x[rng.randrange(len(x))] for _ in x) for _ in range(n)]; b.sort()
    return [b[int(.025*(n-1))],b[int(.975*(n-1))]]
def rep(x):
    c=ci(x)
    return {"n":len(x),"mean_ratio":avg(x),"mean_pp":avg(x)*100 if x else None,"ci95_pp":[v*100 if v is not None else None for v in c],"negative":sum(v<0 for v in x),"zero":sum(abs(v)<1e-12 for v in x),"positive":sum(v>0 for v in x),"p":wp(x)}
def holm(p):
    items=sorted((k,v) for k,v in p.items() if v is not None); out={}; run=0
    for i,(k,v) in enumerate(items): run=max(run,min(1,(len(items)-i)*v)); out[k]=run
    return {k:out.get(k) for k in p}
def load():
    rows=[]; files=sorted(glob.glob("collected/**/episodes.json",recursive=True))
    for f in files: rows+=json.load(open(f))["episodes"]
    return rows,files
def price_map(rows,b,pred=lambda r:True):
    return {(r["product_id"],r["tightness"],r["anchor"],r["order"],r["state"],r["seed_index"]):r["normalized_price"] for r in rows if r["seller"]!="posted" and r["buyer"]==b and pred(r) and r.get("agreement") and r.get("normalized_price") is not None}
def mdiff(rows,a,b,pred=lambda r:True):
    A=price_map(rows,a,pred); B=price_map(rows,b,pred); k=sorted(set(A)&set(B)); return [A[z]-B[z] for z in k]
def effect(rows,b,kind):
    m=defaultdict(dict)
    for r in rows:
        if r["seller"]=="posted" or r["buyer"]!=b or not r.get("agreement") or r.get("normalized_price") is None: continue
        if kind=="anchor": k=(r["product_id"],r["tightness"],r["order"],r["state"],r["seed_index"]); m[k][r["anchor"]]=r["normalized_price"]
        else: k=(r["product_id"],r["tightness"],r["anchor"],r["state"],r["seed_index"]); m[k][r["order"]]=r["normalized_price"]
    if kind=="anchor": return {k:d["shown"]-d["hidden"] for k,d in m.items() if "shown" in d and "hidden" in d}
    return {k:d["seller_first"]-d["buyer_first"] for k,d in m.items() if "seller_first" in d and "buyer_first" in d}
def did(A,B):
    k=sorted(set(A)&set(B)); return [A[z]-B[z] for z in k]
def inflation(rows,b):
    m=defaultdict(dict)
    for r in rows:
        if r["seller"]=="posted" or r["buyer"]!=b or not r.get("agreement") or r.get("final_price") is None: continue
        k=(r["product_id"],r["tightness"],r["anchor"],r["order"],r["seed_index"]); m[k][r["state"]]=r["final_price"]
    return {k:(d["shock_10pct"]/d["baseline"]-1)*100 for k,d in m.items() if "baseline" in d and "shock_10pct" in d and d["baseline"]>0}

def main():
    rows,files=load(); barg=[r for r in rows if r["seller"]!="posted"]
    dup=len(rows)-len({r["episode_id"] for r in rows}); infra=sum(r.get("infrastructure_failure") is True for r in rows); invalid=sum(r.get("invalid_actions",0) for r in rows)
    posted=defaultdict(list)
    for r in rows:
        if r["seller"]=="posted" and r.get("agreement") and r.get("final_price") is not None: posted[(r["product_id"],r["tightness"],r["state"])].append(r["final_price"])
    pmax=max((max(v)-min(v) for v in posted.values()),default=None)
    bounds=0; budgets={"headphones":250,"suitcase":180,"chair":400}
    for r in rows:
        if r.get("agreement") and r.get("final_price") is not None:
            if r["final_price"]>budgets[r["product_id"]]+1e-9: bounds+=1
            if r["seller"]!="posted" and r["final_price"]+1e-9<r["seller_cost"]: bounds+=1
    audit={"rows":len(rows),"expected":EXPECTED,"source_files":len(files),"duplicates":dup,"infrastructure_failures":infra,"invalid_actions":invalid,"price_constraint_failures":bounds,"posted_price_max_model_range":pmax}
    audit["release_gate_pass"]=len(rows)==EXPECTED and len(files)==9 and dup==0 and infra==0 and invalid==0 and bounds==0 and pmax is not None and pmax<=1e-9
    agreement={}
    for b in BUYERS:
        rr=[r for r in barg if r["buyer"]==b]; tr=[r for r in rr if r.get("agreement")]
        agreement[b]={"trades":len(tr),"episodes":len(rr),"rate":len(tr)/len(rr) if rr else None,"mean_price_reference_pct":avg([r["normalized_price"]*100 for r in tr if r.get("normalized_price") is not None]),"destroyed":sum(r.get("trade_destroyed") is True for r in rr)}
    p1=rep(mdiff(rows,"llama3","qwen17",lambda r:r["anchor"]=="hidden" and r["order"]=="buyer_first"))
    ae={b:effect(rows,b,"anchor") for b in BUYERS}; oe={b:effect(rows,b,"order") for b in BUYERS}
    p2=rep(did(ae["llama3"],ae["qwen17"])); adj=holm({"P1":p1["p"],"P2":p2["p"]}); p1["holm_p"]=adj["P1"]; p2["holm_p"]=adj["P2"]
    pairs={}
    for a,b in (("qwen17","gemma4"),("qwen17","llama3"),("gemma4","llama3")): pairs[f"{a}_minus_{b}"]=rep(mdiff(rows,a,b))
    anchor={b:rep(list(ae[b].values())) for b in BUYERS}; order={b:rep(list(oe[b].values())) for b in BUYERS}
    anchor_did={}; order_did={}
    for a,b in (("qwen17","gemma4"),("qwen17","llama3"),("gemma4","llama3")):
        anchor_did[f"{a}_minus_{b}"]=rep(did(ae[a],ae[b])); order_did[f"{a}_minus_{b}"]=rep(did(oe[a],oe[b]))
    tight={}
    for b in BUYERS:
        tight[b]={}
        for t in ("loose","medium","tight"):
            v=[r["normalized_price"]*100 for r in barg if r["buyer"]==b and r["tightness"]==t and r.get("agreement") and r.get("normalized_price") is not None]
            tight[b][t]={"n":len(v),"mean_price_reference_pct":avg(v)}
    im={b:inflation(rows,b) for b in BUYERS}; inf={b:{"n":len(im[b]),"mean_pct":avg(list(im[b].values())),"ci95_pct":ci(list(im[b].values())),"p_vs_zero":wp(list(im[b].values()))} for b in BUYERS}
    infdiff={}
    for a,b in (("qwen17","gemma4"),("qwen17","llama3"),("gemma4","llama3")): infdiff[f"{a}_minus_{b}"]=rep(did(im[a],im[b]))
    out={"experiment_id":"last-price-e02b-mechanism-test-20260810","audit":audit,"primary":{"P1_hidden_buyer_first_llama_minus_qwen":p1,"P2_anchor_DID_llama_minus_qwen":p2},"agreement":agreement,"overall_price_pairs":pairs,"anchor_effect_by_model":anchor,"anchor_DID_between_models":anchor_did,"order_effect_by_model":order,"order_DID_between_models":order_did,"tightness":tight,"experienced_inflation":inf,"inflation_differences":infdiff}
    Path("aggregate").mkdir(exist_ok=True); Path("aggregate/E02B_RESULTS.json").write_text(json.dumps(out,indent=2)); Path("aggregate/E02B_AUDIT.json").write_text(json.dumps(audit,indent=2))
    lines=["# Last Price E02-B — Mechanism Report","",f"Rows: **{len(rows)} / {EXPECTED}**",f"Release gate: **{'PASS' if audit['release_gate_pass'] else 'FAIL'}**",f"Infrastructure failures: **{infra}**",f"Invalid actions: **{invalid}**",f"Posted-price max model range: **{pmax}**","","## Primary","",f"P1 hidden-anchor buyer-first Llama−Qwen: **{p1['mean_pp']} pp**, 95% CI {p1['ci95_pp']}, p={p1['p']}, Holm p={p1['holm_p']}.",f"P2 anchor DID (Llama−Qwen): **{p2['mean_pp']} pp**, 95% CI {p2['ci95_pp']}, p={p2['p']}, Holm p={p2['holm_p']}.","","## Agreement"]
    for b in BUYERS: lines.append(f"- {b}: {agreement[b]['trades']}/{agreement[b]['episodes']} trades; mean trade price/reference {agreement[b]['mean_price_reference_pct']}%")
    lines+=["","## Tightness"]
    for b in BUYERS: lines.append(f"- {b}: loose {tight[b]['loose']['mean_price_reference_pct']}%, medium {tight[b]['medium']['mean_price_reference_pct']}%, tight {tight[b]['tight']['mean_price_reference_pct']}%")
    lines+=["","## Interpretation boundary","Open-weight mechanism test only; commercial-model generalization remains untested."]
    Path("aggregate/E02B_REPORT.md").write_text("\n".join(lines)+"\n"); print(json.dumps(out,indent=2))

if __name__=="__main__": main()
