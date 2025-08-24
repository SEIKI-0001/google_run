from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
@app.get("/healthz")
def healthz():
    return {"ok": True}

class GenReq(BaseModel):
    user_id: str | None = None
    message: str | None = None

@app.post("/generate")
def generate(req: GenReq):
    # まずは動作確認用のダミー応答
    return {"echo": {"user_id": req.user_id, "message": req.message}, "ok": True}
