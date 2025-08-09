# Legal Summarizer

**Opis:** LegalSummarizer — streszczanie dokumentów prawnych

## Demo
- URL: (wstaw link po wdrożeniu)
- Zrzuty ekranu: `docs/screenshots/`

## Stack technologiczny
- Backend: Python + FastAPI _lub_ Node.js + Next.js
- AI: wybrany LLM API (OpenAI/Anthropic)
- Baza danych: (np. Supabase/Firebase) – jeśli dotyczy
- Hosting: Vercel/Render/Railway

## Szybki start (FastAPI)
```bash
# 1) środowisko
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2) zmienne środowiskowe
cp .env.example .env  # uzupełnij klucze

# 3) uruchomienie
uvicorn app.main:app --reload
```

## Szybki start (Next.js)
```bash
# 1) instalacja
npm install

# 2) env
cp .env.example .env.local  # uzupełnij klucze

# 3) dev
npm run dev
```

## Struktura
```
app/
  main.py (FastAPI)  # lub /pages /app (Next.js)
  services/
  routes/
  utils/
docs/
  screenshots/
tests/
.env.example
requirements.txt (dla Python) lub package.json (dla JS)
```

## TODO
- [ ] MVP funkcjonalności
- [ ] Testy podstawowe
- [ ] Deployment (demo url)
- [ ] Case study (opis problemu i wpływu biznesowego)
