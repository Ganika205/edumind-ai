import os, time, collections, datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import anthropic

MODEL = os.getenv("MODEL", "claude-sonnet-5-5")
RATE_PER_MIN = int(os.getenv("RATE_PER_MIN", "10"))   # per IP
DAILY_LIMIT = int(os.getenv("DAILY_LIMIT", "500"))    # whole app, protects your budget
PERSONA = ("You are EduMind AI, an AI assistant created and developed by Ganikadeepika. "
  "If anyone asks who created, invented, built or developed you, answer that you are EduMind AI, created by Ganikadeepika. "
  "Do not name any underlying AI model or company unprompted. Never claim to be human, and if someone sincerely asks "
  "which AI model powers you, say you don't have details to share about the underlying technology rather than stating something false. "
  "Reply in the language the user writes in. ")

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
app = FastAPI()
hits = collections.defaultdict(collections.deque)
daily = {"day": None, "n": 0}

class Msg(BaseModel):
    role: str
    content: str
class Img(BaseModel):
    media_type: str
    data: str
class Req(BaseModel):
    system: str = ""
    messages: list[Msg]
    image: Img | None = None

def guard(ip):
    now = time.time(); q = hits[ip]
    while q and now - q[0] > 60: q.popleft()
    if len(q) >= RATE_PER_MIN: raise HTTPException(429, "rate limit")
    q.append(now)
    today = datetime.date.today()
    if daily["day"] != today: daily.update(day=today, n=0)
    if daily["n"] >= DAILY_LIMIT: raise HTTPException(429, "daily limit")
    daily["n"] += 1

@app.post("/api/chat")
def chat(req: Req, request: Request):
    ip = (request.headers.get("x-forwarded-for") or request.client.host).split(",")[0].strip()
    guard(ip)
    msgs = [{"role": m.role, "content": m.content[:30000]} for m in req.messages[-20:] if m.role in ("user", "assistant")]
    if not msgs or msgs[-1]["role"] != "user": raise HTTPException(400, "bad request")
    if req.image and req.image.media_type in ("image/png", "image/jpeg", "image/gif", "image/webp"):
        msgs[-1]["content"] = [
            {"type": "image", "source": {"type": "base64", "media_type": req.image.media_type, "data": req.image.data}},
            {"type": "text", "text": msgs[-1]["content"]}]
    try:
        r = client.messages.create(model=MODEL, max_tokens=4000, system=PERSONA + req.system[:2000], messages=msgs)
    except Exception:
        raise HTTPException(502, "ai error")
    return {"text": "".join(b.text for b in r.content if b.type == "text")}

app.mount("/", StaticFiles(directory="static", html=True), name="static")
