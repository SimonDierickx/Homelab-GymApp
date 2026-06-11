#!/usr/bin/env python3
"""Gym data receiver — saves workout JSON files to disk."""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json, os, glob

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["https://app.sdckx.be"], allow_methods=["*"], allow_headers=["*"])

API_KEY  = os.getenv("GYM_API_KEY", "change-me-in-env")
DATA_DIR = os.path.expanduser("~/projects/data/gym")
os.makedirs(DATA_DIR, exist_ok=True)

def auth(request: Request):
    if request.headers.get("X-API-Key") != API_KEY:
        raise HTTPException(401, "Unauthorized")

@app.post("/gym/save")
async def save(request: Request):
    auth(request)
    data = await request.json()
    now  = datetime.now()
    user = data.get("user", "unknown")
    sess = data.get("sessionKey", "X")
    fname = f"{now.strftime('%Y-%m-%d_%H-%M')}_{sess}_{user}.json"
    fpath = os.path.join(DATA_DIR, fname)
    with open(fpath, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[gym] Saved: {fname}")
    return {"status": "saved", "file": fname}

@app.get("/gym/history")
async def history(request: Request, user: str = "simon"):
    auth(request)
    pattern = os.path.join(DATA_DIR, f"*_{user}.json")
    files   = sorted(glob.glob(pattern), reverse=True)[:50]
    sessions = []
    for f in files:
        try:
            with open(f) as fh:
                sessions.append(json.load(fh))
        except Exception:
            pass
    return sessions

@app.get("/gym/health")
async def health():
    return {"status": "ok"}
