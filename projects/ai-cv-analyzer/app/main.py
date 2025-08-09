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
