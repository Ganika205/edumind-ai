# EduMind AI – Deploy guide (Render, ஒரே service)

## 1. API key
console.anthropic.com -> API key உருவாக்குங்க. Billing-ல monthly spend limit கண்டிப்பா வைங்க.

## 2. GitHub
இந்த folder-ஐ ஒரு புது GitHub repo-ல upload பண்ணுங்க (.env upload பண்ணாதீங்க).

## 3. Render
1. render.com -> New -> Web Service -> உங்க repo-ஐ select பண்ணுங்க.
2. Build: `pip install -r requirements.txt`
3. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Environment -> `ANTHROPIC_API_KEY` = உங்க key.
5. Deploy -> `https://edumind-ai.onrender.com` மாதிரி public link கிடைக்கும்.

## 4. Local test
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=your-key
    uvicorn main:app --reload     # http://localhost:8000

## Limits (செலவு பாதுகாப்பு)
`RATE_PER_MIN` (ஒரு IP-க்கு நிமிஷத்துக்கு) மற்றும் `DAILY_LIMIT` (ஒரு நாளுக்கு மொத்தம்) environment variables-ல மாத்தலாம்.
Free Render plan-ல app தூங்கி எழ 30-60 வினாடி ஆகலாம்.

## அடுத்த stages
Login (Supabase/Firebase), saved history (PostgreSQL), PDF/DOCX reading, live web search.
