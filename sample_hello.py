# sample_hello.py に追記
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
    # まずは動作確認用のダミー
    return {"plan": [{"WBS":"wbs0","Task Name":"sample","Date":"2025-08-25","Day":"Mon","Duration":60,"Status":"未着手"}],
            "echo": req.model_dump()}
