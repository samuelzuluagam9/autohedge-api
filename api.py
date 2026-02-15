import os
import uuid
from typing import Dict, Optional, List

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from autohedge import AutoFund  # matches the PDF usage :contentReference[oaicite:2]{index=2}

app = FastAPI(title="AutoHedge API")

# Simple in-memory API key store (fine for demo; resets on redeploy)
API_KEYS: Dict[str, Dict] = {}


class UserCreate(BaseModel):
    username: str
    email: str
    fund_name: str
    fund_description: str


class TradeRequest(BaseModel):
    stocks: List[str] = ["NVDA"]
    task: str
    allocation: Optional[float] = None
    strategy_type: Optional[str] = None
    risk_level: Optional[int] = None


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/users")
def create_user(payload: UserCreate):
    api_key = uuid.uuid4().hex
    API_KEYS[api_key] = payload.model_dump()
    return {"api_key": api_key}


@app.post("/trades")
def trigger_trade(req: TradeRequest, x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")):
    if not x_api_key or x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Build a richer task string if optional fields provided
    extra = []
    if req.allocation is not None:
        extra.append(f"allocation={req.allocation}")
    if req.strategy_type:
        extra.append(f"strategy={req.strategy_type}")
    if req.risk_level is not None:
        extra.append(f"risk_level={req.risk_level}")
    task = req.task if not extra else f"{req.task} ({', '.join(extra)})"

    trading_system = AutoFund(req.stocks)  # matches PDF :contentReference[oaicite:3]{index=3}
    result = trading_system.run(task=req.task)
    return {"result": result}


@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)
