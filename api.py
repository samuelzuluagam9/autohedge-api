import os
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from autohedge import AutoFund
from fastapi.responses import Response
app = FastAPI(title="AutoHedge API")

# Simple protection so random people don’t burn your credits
API_PASSWORD = os.getenv("API_PASSWORD")

class RunRequest(BaseModel):
    stocks: list[str] = ["NVDA"]
    task: str

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/run")
def run(req: RunRequest, x_api_key: str | None = Header(default=None)):
    if API_PASSWORD:
        if not x_api_key or x_api_key != API_PASSWORD:
            raise HTTPException(status_code=401, detail="Unauthorized")

    trading_system = AutoFund(req.stocks)
    result = trading_system.run(task=req.task)
    return {"result": result}
@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)
