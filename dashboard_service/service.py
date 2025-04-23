from flask import Flask, jsonify, request, render_template_string
import os, redis, json, datetime

REDIS_HOST    = os.getenv("REDIS_HOST", "redis")
REDIS_PORT    = 6379
RAW_KEY       = os.getenv("RAW_REVIEW_KEY", "raw_reviews")
ESC_KEY       = "escalations"

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Sentiment Pipeline Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<style>
  body{background:#0a0a0a;color:#f5f5f5;font-family:"Segoe UI",system-ui,sans-serif;margin:0;padding:1.25rem}
  h1{color:#28e470;margin-top:0}
  input,textarea{background:#202020;border:1px solid #444;color:#f5f5f5;font:inherit;padding:.25rem .4rem;border-radius:2px;width:100%}
  textarea{height:7rem}
  button{background:#22c55e;border:0;color:#0a0a0a;font-weight:600;padding:.4rem 1.2rem;border-radius:4px;cursor:pointer}
  button:disabled{opacity:.5;cursor:default}
  table{width:100%;border-collapse:collapse;margin-top:.5rem}
  th,td{border:1px solid #333;padding:.4rem .6rem;text-align:left}
  tr:nth-child(odd){background:#111}
  tr.escalated{background:#4b0000}
  .pill{display:inline-block;background:#16a34a;color:#fff;padding:.18rem .6rem;border-radius:999px;font-size:.82rem;margin-right:.3rem;cursor:pointer}
  .pill.danger{background:#dc2626}
</style>
</head>
<body>
<h1>⚡ Sentiment Pipeline Dashboard</h1>
<p><a href="/api/escalations">/api/escalations</a> returns raw JSON.</p>
<p>
  Debug keys:
  <a href="/api/redis/raw_reviews">raw_reviews</a> •
  <a href="/api/redis/classified_reviews">classified_reviews</a> •
  <a href="/api/redis/cooldown_state">cooldown_state</a>
</p>

<h2>Submit a quick review</h2>
<form id="reviewForm">
  <label>Product ID
    <input id="pid" value="widget-A" required>
  </label><br>
  <label>Text<br>
    <textarea id="text" placeholder="Great product!" required></textarea>
  </label><br>
  <button id="sendBtn" type="submit">Send →</button>
  <span id="status"></span>
</form>

<h2>Sample batches</h2>
<button class="pill danger"  onclick="loadSample('A')">Widget A 🔥 (all negative)</button>
<button class="pill"          onclick="loadSample('B')">Widget B ± (mixed)</button>

<h2>Live Escalations</h2>
<table id="escTable">
  <thead><tr><th>Product</th><th>Reason</th><th>When (UTC)</th></tr></thead>
  <tbody></tbody>
</table>

<script>
const api = {ingest: "{{ ingest_url }}", esc: "/api/escalations"}
const form   = document.getElementById("reviewForm")
const pidEl  = document.getElementById("pid")
const textEl = document.getElementById("text")
const btn    = document.getElementById("sendBtn")
const status = document.getElementById("status")
const table  = document.getElementById("escTable").querySelector("tbody")

// ----- helpers -----
function mark(msg, ok=true){
  status.textContent = msg
  status.style.color = ok ? "#22c55e" : "#f87171"
}
function clearStatus(){ status.textContent = "" }

async function refreshEscalations(){
  const res  = await fetch(api.esc)
  const data = await res.json()
  table.innerHTML = ""
  Object.values(data).flat().forEach(e => {
    const tr = table.insertRow(-1)
    tr.className = "escalated"
    tr.insertCell().textContent = e.product_id
    tr.insertCell().textContent = e.reason
    tr.insertCell().textContent = e.escalated_at
  })
}
refreshEscalations()
setInterval(refreshEscalations, 10000) // 10-s poll

// ----- form -----
form.addEventListener("submit", async ev => {
  ev.preventDefault()
  clearStatus(); btn.disabled = true
  try{
    const body = {product_id: pidEl.value.trim(), text: textEl.value.trim()}
    const res  = await fetch(api.ingest,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)})
    if(!res.ok) throw Error((await res.json()).error || res.status)
    mark("sent")
    textEl.value = ""                 // clear textbox
    await refreshEscalations()        // immediate table refresh
  }catch(err){ mark("✗ "+err,false) }
  finally{ btn.disabled = false }
})

// allow ENTER to submit unless SHIFT/CTRL pressed (which lets you add newline)
form.addEventListener("keydown", ev => {
  if(ev.key==="Enter" && !ev.shiftKey && !ev.ctrlKey){
    if(document.activeElement === textEl){ ev.preventDefault(); btn.click() }
  }
})

// ----- sample batches -----
const samples = {
  A: Array.from({length:3},(_,i)=>({product_id:"widget-x",text:`Terrible product #${i+1}` })),
  B: [
        {product_id:"widget-y",text:"Love it!"},
        {product_id:"widget-y",text:"Meh, could be better."},
        {product_id:"widget-y",text:"Absolutely awful."},
     ]
}
async function loadSample(letter){
  for(const r of samples[letter]){
    await fetch(api.ingest,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(r)})
  }
  await refreshEscalations()
}
</script>
</body>
</html>
'''

def _fetch_redis(key: str, fallback="{}"):
    """
    Return the JSON value stored at `key` (decoded), or fallback if missing/invalid.
    """
    try:
        import redis, json
        red = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        raw = red.get(key) or fallback
        return json.loads(raw)
    except Exception as e:
        # Return empty structure + error note so the caller sees *something*
        return {"_error": str(e), "_key": key}
    
@app.route("/")
def home():
    ingest_url = os.getenv("INGEST_URL", "http://localhost:5000/submit_review")
    return render_template_string(HTML, ingest_url=ingest_url)

# ---------- API -----------
@app.route("/api/escalations")
def api_escalations():
    raw = r.get(ESC_KEY)
    return jsonify(json.loads(raw) if raw else {})

@app.route("/health")
def health():
    return jsonify(status="ok")

@app.route("/api/redis/<key>")
def api_any_redis(key):
    """
    Generic inspector – fetches and returns the specified Redis key as JSON.
    Useful for debugging:  
      • /api/redis/raw_reviews  
      • /api/redis/classified_reviews  
      • /api/redis/cooldown_state  
    """
    return jsonify(_fetch_redis(key))


# ---------- server ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, threaded=False)
