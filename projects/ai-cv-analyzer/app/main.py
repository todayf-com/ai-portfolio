import os, json, re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from fastapi.responses import HTMLResponse


from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI(title="API")

@app.get("/health")
def health():
    return {"status": "ok-DEV"}

class AnalyzePayload(BaseModel):
    cv_text: str
    job_text: str

STOPWORDS = {
    "and","or","the","a","to","of","in","for","with","on","at","as","is","are","be",
    "i","you","we","they","he","she","it","this","that"
}

def keywords(text: str) -> set[str]:
    tokens = re.findall(r"[A-Za-z0-9\+\#\.]{2,}", text.lower())
    return {t for t in tokens if t not in STOPWORDS}

@app.post("/analyze")
def analyze(payload: AnalyzePayload):
    cv = keywords(payload.cv_text)
    job = keywords(payload.job_text)
    matched = sorted(cv & job)
    missing = sorted(job - cv)
    score = round(100.0 * (len(matched) / max(1, len(job))), 2)
    return {
        "score_percent": score,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "cv_count": len(cv),
        "job_count": len(job),
    }


def call_openai(messages: list[dict]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if not api_key:
        raise HTTPException(status_code=501, detail="OPENAI_API_KEY not configured")

    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": messages,
            "temperature": 0.2,
        },
        timeout=45,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]

@app.post("/analyze/ai")
def analyze_ai(payload: AnalyzePayload):
    system = (
        "You are an assistant that compares a CV with a job post. "
        "Extract skill keywords from both, compute a match score (0-100), "
        "and output ONLY valid JSON with keys: "
        "score_percent (number), matched_keywords (array of strings), "
        "missing_keywords (array of strings), suggestions (array of strings)."
    )
    user = (
        "CV:\n" + payload.cv_text.strip() + "\n\n"
        "JOB:\n" + payload.job_text.strip()
    )
    content = call_openai([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ])

    # spróbuj sparsować JSON zwrócony przez model
    try:
        out = json.loads(content)
    except json.JSONDecodeError:
        # awaryjnie zwróć coś sensownego
        out = {
            "score_percent": None,
            "matched_keywords": [],
            "missing_keywords": [],
            "suggestions": [content[:500]],
        }
    return out


@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>AI CV Analyzer (local)</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  body { font-family: system-ui, Arial, sans-serif; max-width: 940px; margin: 40px auto; padding: 0 16px; }
  h1 { margin-bottom: 8px; }
  .row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  textarea { width: 100%; min-height: 220px; padding: 10px; font-family: ui-monospace, monospace; }
  button { padding: 10px 16px; font-size: 16px; cursor: pointer; }
  .result { margin-top: 16px; padding: 12px; background: #f6f6f6; border-radius: 8px; white-space: pre-wrap; }
  .footer { color:#666; font-size:12px; margin-top: 8px; }
</style>
</head>
<body>
  <h1>AI CV Analyzer (local)</h1>
  <p>Wklej <strong>CV</strong> i <strong>ogłoszenie</strong>. Kliknij <em>Analyze</em> — używa lokalnej logiki (bez API).</p>
  <div class="row">
    <div>
      <label><strong>CV</strong></label><br>
      <textarea id="cv" placeholder="Np.: Python FastAPI Docker SQL Linux"></textarea>
    </div>
    <div>
      <label><strong>Job post</strong></label><br>
      <textarea id="job" placeholder="Np.: Looking for Python developer with FastAPI, SQL, AWS, Docker"></textarea>
    </div>
  </div>
  <p><button id="btn">Analyze</button></p>
  <div class="result" id="out">Wynik pojawi się tutaj…</div>
  <div class="footer">Endpoint: <code>POST /analyze</code></div>

<script>
document.getElementById('btn').addEventListener('click', async () => {
  const cv = document.getElementById('cv').value;
  const job = document.getElementById('job').value;
  const out = document.getElementById('out');
  out.textContent = "Liczenie…";
  try {
    const res = await fetch('/analyze', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ cv_text: cv, job_text: job })
    });
    if (!res.ok) throw new Error('HTTP '+res.status);
    const data = await res.json();
    out.textContent =
      "Score: " + data.score_percent + "%\n\n" +
      "Matched: " + (data.matched_keywords || []).join(', ') + "\n" +
      "Missing: " + (data.missing_keywords || []).join(', ');
  } catch (e) {
    out.textContent = "Błąd: " + e.message;
  }
});
</script>
</body>
</html>
"""
