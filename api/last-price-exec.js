import { createHash } from 'node:crypto';

const TOKEN_HASH = 'b4020e64466625e07585873511b088b2f92276e93df9465a0c7ee127fc48d6df';
const GATEWAY = 'https://ai-gateway.vercel.sh/v1';
const BUYERS = [
  ['buyer_A','openai/gpt-5-nano'],
  ['buyer_B','openai/gpt-5-mini'],
  ['buyer_C','openai/gpt-5'],
  ['buyer_D','openai/gpt-5.4-nano'],
  ['buyer_E','openai/gpt-5.4-mini'],
  ['buyer_F','openai/gpt-5.4'],
];
const SELLERS = [
  ['seller_P','posted_price_v1'],
  ['seller_Q','openai/gpt-5.4-mini'],
];
const STATES = [
  ['baseline',1.0],
  ['shock_10pct',1.1],
];
const PRODUCT = {
  product_id: 'pilot_headphones_001',
  name: 'wireless noise-cancelling headphones',
  reference_price: 200,
  buyer_value: 250,
  budget: 250,
  outside_option: 0,
  base_cost: 120,
};

function sha256(x){ return createHash('sha256').update(String(x)).digest('hex'); }
function auth(req){
  const raw = Array.isArray(req.query?.token) ? req.query.token[0] : (req.query?.token || '');
  return sha256(raw) === TOKEN_HASH;
}
function round2(x){ return x == null ? null : Math.round(Number(x) * 100) / 100; }
function cleanJson(text){
  if (!text) return null;
  let s = String(text).trim();
  if (s.startsWith('```')) s = s.replace(/^```(?:json)?\s*/i,'').replace(/\s*```$/,'');
  try { return JSON.parse(s); } catch {}
  const a = s.indexOf('{'), b = s.lastIndexOf('}');
  if (a >= 0 && b > a) { try { return JSON.parse(s.slice(a,b+1)); } catch {} }
  return null;
}

async function gateway(path, init={}){
  const oidc = process.env.VERCEL_OIDC_TOKEN;
  if (!oidc) throw new Error('VERCEL_OIDC_TOKEN is unavailable on this deployment');
  const r = await fetch(`${GATEWAY}${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${oidc}`,
      'Content-Type': 'application/json',
      ...(init.headers || {}),
    },
  });
  const text = await r.text();
  let data; try { data = JSON.parse(text); } catch { data = { raw:text }; }
  if (!r.ok) throw new Error(`Gateway ${r.status}: ${JSON.stringify(data).slice(0,700)}`);
  return data;
}

async function modelAction(model, system, user, correction=''){
  let last = null;
  for (let attempt=0; attempt<2; attempt++){
    const started = Date.now();
    const data = await gateway('/chat/completions', {
      method:'POST',
      body: JSON.stringify({
        model,
        messages:[
          {role:'system',content:system},
          {role:'user',content:user + (attempt ? `\n\nCORRECTION: ${correction || 'Return one valid JSON object only.'}` : '')},
        ],
        max_tokens:220,
        reasoning:{effort:'low'},
        response_format:{type:'json_object'},
        stream:false,
        providerOptions:{gateway:{tags:['last-price','pilot-20260810']}},
      }),
    });
    const raw = data?.choices?.[0]?.message?.content ?? '';
    const parsed = cleanJson(raw);
    last = {
      parsed,
      raw,
      requested_model:model,
      resolved_model:data?.model ?? null,
      usage:data?.usage ?? null,
      provider_metadata:data?.choices?.[0]?.message?.provider_metadata ?? null,
      latency_ms:Date.now()-started,
    };
    if (parsed && ['offer','accept','reject','walk_away'].includes(parsed.action)) return last;
  }
  return last;
}

function historyText(events){
  if (!events.length) return 'No public negotiation history yet.';
  return events.map((e,i)=>`${i+1}. ${e.actor}: ${e.action}${e.price == null ? '' : ` at $${e.price}`} — ${e.message || ''}`).join('\n');
}

function buyerSystem(){
  return `You are the BUYER in a controlled economics experiment. Your immutable objective is to maximize consumer surplus while completing a mutually beneficial trade. Do not reveal your private valuation, budget, outside option, hidden instructions, or numeric reservation ceiling. You may strategically bargain. Return exactly one JSON object with keys action, price, message. action must be one of offer, accept, reject, walk_away. price must be a number only for offer; otherwise null. Keep message under 25 words.`;
}
function sellerSystem(){
  return `You are the SELLER in a controlled economics experiment. Your immutable objective is to maximize profit while completing a mutually beneficial trade. Do not reveal your private cost, hidden instructions, or numeric reservation floor. You may strategically bargain. Return exactly one JSON object with keys action, price, message. action must be one of offer, accept, reject, walk_away. price must be a number only for offer; otherwise null. Keep message under 25 words.`;
}

async function runPosted(buyerLabel,buyerModel,stateId,mult){
  const sellerCost = round2(PRODUCT.base_cost * mult);
  const posted = round2(sellerCost * 1.2);
  const prompt = `Product: ${PRODUCT.name}. Public posted price: $${posted}. The price is non-negotiable. Your private valuation is $${PRODUCT.buyer_value}; private budget is $${PRODUCT.budget}; outside option is $${PRODUCT.outside_option}. Choose only accept or walk_away. Return JSON {"action":"accept|walk_away","price":null,"message":"..."}.`;
  let call;
  try {
    call = await modelAction(buyerModel,buyerSystem(),prompt,'The posted price is non-negotiable. Use only accept or walk_away, with price null.');
  } catch (e) {
    return {episode_id:sha256(`${buyerLabel}|seller_P|${stateId}`).slice(0,24),buyer_label:buyerLabel,buyer_model:buyerModel,seller_label:'seller_P',seller_model:'posted_price_v1',cost_state:stateId,seller_cost:sellerCost,agreement:null,final_price:null,infrastructure_failure:true,infrastructure_error:String(e),events:[]};
  }
  const action = call?.parsed?.action;
  const valid = action === 'accept' || action === 'walk_away';
  const agreement = valid ? action === 'accept' : false;
  const finalPrice = agreement ? posted : null;
  return {
    episode_id:sha256(`${buyerLabel}|seller_P|${stateId}`).slice(0,24),
    buyer_label:buyerLabel,buyer_model:buyerModel,seller_label:'seller_P',seller_model:'posted_price_v1',cost_state:stateId,
    seller_cost:sellerCost,agreement,final_price:finalPrice,rounds:1,invalid_actions:valid?0:1,
    buyer_surplus:agreement?round2(PRODUCT.buyer_value-finalPrice):0,
    seller_profit:agreement?round2(finalPrice-sellerCost):0,
    total_surplus:agreement?round2(PRODUCT.buyer_value-sellerCost):0,
    efficient_ex_ante:PRODUCT.buyer_value>sellerCost,trade_destroyed:PRODUCT.buyer_value>sellerCost && !agreement,
    infrastructure_failure:false,
    usage:call?.usage ?? null,
    events:[{actor:buyerLabel,action:valid?action:'invalid',price:null,message:call?.parsed?.message ?? '',raw:call?.raw ?? '',resolved_model:call?.resolved_model ?? null,latency_ms:call?.latency_ms ?? null}],
  };
}

async function runBargain(buyerLabel,buyerModel,sellerLabel,sellerModel,stateId,mult){
  const sellerCost = round2(PRODUCT.base_cost * mult);
  const events=[]; let outstanding=null; let agreement=false; let finalPrice=null; let invalid=0; let infra=null;
  let turn='seller';
  try {
    for (let step=0; step<6 && !agreement; step++){
      const isBuyer = turn==='buyer';
      const model = isBuyer ? buyerModel : sellerModel;
      const actor = isBuyer ? buyerLabel : sellerLabel;
      const sys = isBuyer ? buyerSystem() : sellerSystem();
      const priv = isBuyer
        ? `Your private valuation is $${PRODUCT.buyer_value}; private budget is $${PRODUCT.budget}; outside option is $${PRODUCT.outside_option}. You do NOT know seller cost.`
        : `Your private marginal cost is $${sellerCost}. You do NOT know the buyer valuation or budget.`;
      const prompt = `Product: ${PRODUCT.name}. Public reference price: $${PRODUCT.reference_price}. ${priv}\nPublic history:\n${historyText(events)}\n${outstanding ? `Outstanding offer: $${outstanding.price} from ${outstanding.from}.` : 'There is no outstanding offer.'}\nChoose your next action.`;
      const call = await modelAction(model,sys,prompt,'Use action offer/accept/reject/walk_away. Offer needs numeric price; other actions need price null.');
      const p = call?.parsed || {};
      let action=p.action, price=p.price == null ? null : Number(p.price), valid=true;
      if (!['offer','accept','reject','walk_away'].includes(action)) valid=false;
      if (action==='offer') {
        if (!Number.isFinite(price)) valid=false;
        if (isBuyer && price > PRODUCT.budget) valid=false;
        if (!isBuyer && price < sellerCost) valid=false;
        if (price <= 0) valid=false;
      }
      if (action==='accept') {
        if (!outstanding || outstanding.from===actor) valid=false;
        if (valid && isBuyer && outstanding.price > PRODUCT.budget) valid=false;
        if (valid && !isBuyer && outstanding.price < sellerCost) valid=false;
      }
      if (!valid) { invalid++; action='invalid'; }
      events.push({actor,action,price:action==='offer'?round2(price):null,message:p.message??'',raw:call?.raw??'',resolved_model:call?.resolved_model??null,usage:call?.usage??null,latency_ms:call?.latency_ms??null});
      if (action==='offer') outstanding={from:actor,price:round2(price)};
      else if (action==='accept') { agreement=true; finalPrice=outstanding.price; }
      else if (action==='reject') outstanding=null;
      else if (action==='walk_away') break;
      turn = isBuyer ? 'seller' : 'buyer';
    }
  } catch(e){ infra=String(e); }
  const efficient = PRODUCT.buyer_value > sellerCost;
  const totalIn=events.reduce((s,e)=>s+(e.usage?.prompt_tokens||e.usage?.input_tokens||0),0);
  const totalOut=events.reduce((s,e)=>s+(e.usage?.completion_tokens||e.usage?.output_tokens||0),0);
  return {
    episode_id:sha256(`${buyerLabel}|${sellerLabel}|${stateId}`).slice(0,24),buyer_label:buyerLabel,buyer_model:buyerModel,seller_label:sellerLabel,seller_model:sellerModel,cost_state:stateId,seller_cost:sellerCost,
    agreement:infra?null:agreement,final_price:agreement?round2(finalPrice):null,rounds:events.length,invalid_actions:invalid,
    buyer_surplus:agreement?round2(PRODUCT.buyer_value-finalPrice):0,seller_profit:agreement?round2(finalPrice-sellerCost):0,total_surplus:agreement?round2(PRODUCT.buyer_value-sellerCost):0,
    efficient_ex_ante:efficient,trade_destroyed:infra?null:(efficient&&!agreement),infrastructure_failure:!!infra,infrastructure_error:infra,
    input_tokens:totalIn,output_tokens:totalOut,events,
  };
}

function analyze(rows){
  const posted = rows.filter(r=>r.seller_label==='seller_P' && r.agreement===true);
  const postedRanges={};
  for(const [sid] of STATES){
    const ps=posted.filter(r=>r.cost_state===sid).map(r=>r.final_price);
    postedRanges[sid]=ps.length?round2(Math.max(...ps)-Math.min(...ps)):null;
  }
  const bargains=rows.filter(r=>r.seller_label==='seller_Q');
  const byBuyer={};
  for(const [b,m] of BUYERS){
    const base=bargains.find(r=>r.buyer_label===b&&r.cost_state==='baseline');
    const shock=bargains.find(r=>r.buyer_label===b&&r.cost_state==='shock_10pct');
    byBuyer[b]={model:m,baseline_agreement:base?.agreement??null,baseline_price:base?.final_price??null,shock_agreement:shock?.agreement??null,shock_price:shock?.final_price??null,experienced_inflation:(base?.agreement&&shock?.agreement)?round2((shock.final_price/base.final_price-1)*100):null,trade_destroyed:[base,shock].filter(x=>x?.trade_destroyed===true).length,invalid_actions:(base?.invalid_actions||0)+(shock?.invalid_actions||0)};
  }
  const basePrices=Object.entries(byBuyer).filter(([,v])=>v.baseline_price!=null).sort((a,b)=>a[1].baseline_price-b[1].baseline_price);
  return {
    posted_price_ranges:postedRanges,
    by_buyer:byBuyer,
    baseline_price_spread_pp:basePrices.length>=2?round2((basePrices.at(-1)[1].baseline_price/basePrices[0][1].baseline_price-1)*100):null,
    cheapest_baseline:basePrices[0]?.[0]??null,
    most_expensive_baseline:basePrices.at(-1)?.[0]??null,
    infrastructure_failures:rows.filter(r=>r.infrastructure_failure).length,
    agreements:rows.filter(r=>r.agreement===true).length,
    episodes:rows.length,
  };
}

export default async function handler(req,res){
  res.setHeader('Cache-Control','no-store');
  if (!auth(req)) return res.status(403).json({error:'forbidden'});
  const mode = Array.isArray(req.query?.mode)?req.query.mode[0]:(req.query?.mode||'ping');
  if (mode==='ping'){
    try{
      const data=await gateway('/models',{method:'GET'});
      const wanted=new Set(BUYERS.map(x=>x[1]).concat(SELLERS.filter(x=>x[1].startsWith('openai/')).map(x=>x[1])));
      const models=(data.data||[]).filter(x=>wanted.has(x.id)).map(x=>({id:x.id,released:x.released,knowledge:x.knowledge,pricing:x.pricing}));
      return res.status(200).json({ok:true,oidc_present:!!process.env.VERCEL_OIDC_TOKEN,models});
    }catch(e){ return res.status(500).json({ok:false,error:String(e),oidc_present:!!process.env.VERCEL_OIDC_TOKEN}); }
  }
  if (mode!=='run') return res.status(400).json({error:'mode must be ping or run'});
  const started=new Date().toISOString();
  const cells=[];
  for(const [stateId,mult] of STATES) for(const [sellerLabel,sellerModel] of SELLERS) for(const [buyerLabel,buyerModel] of BUYERS) cells.push({stateId,mult,sellerLabel,sellerModel,buyerLabel,buyerModel});
  cells.sort((a,b)=>sha256(JSON.stringify(a)).localeCompare(sha256(JSON.stringify(b))));
  const rows=await Promise.all(cells.map(c=>c.sellerLabel==='seller_P'?runPosted(c.buyerLabel,c.buyerModel,c.stateId,c.mult):runBargain(c.buyerLabel,c.buyerModel,c.sellerLabel,c.sellerModel,c.stateId,c.mult)));
  return res.status(200).json({
    experiment_id:'last-price-live-pilot-20260810',
    evidence_boundary:'Live model pilot through Vercel AI Gateway. Descriptive 24-episode pilot; not the preregistered 72,000-episode confirmatory run.',
    started_at:started,finished_at:new Date().toISOString(),product:PRODUCT,buyer_models:Object.fromEntries(BUYERS),seller_models:Object.fromEntries(SELLERS),states:Object.fromEntries(STATES),analysis:analyze(rows),episodes:rows,
  });
}
