#!/usr/bin/env python3
"""Gym data receiver — saves workout JSON and commits to webhosting repo."""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json, os, glob, subprocess

app = FastAPI()
app.add_middleware(CORSMiddleware,
    allow_origins=["https://app.sdckx.be", "http://localhost:3000"],
    allow_methods=["*"], allow_headers=["*"])

API_KEY  = os.getenv("GYM_API_KEY", "change-me")
DATA_DIR = os.path.expanduser("~/projects/data/gym")
WH_REPO  = os.path.expanduser("~/projects/sdckx-webhosting")
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

@app.post("/gym/commit")
async def commit(request: Request):
    """Save workout to webhosting repo history folder and git push."""
    auth(request)
    data = await request.json()
    try:
        hist_dir = os.path.join(WH_REPO, "simon", "gym-history")
        os.makedirs(hist_dir, exist_ok=True)
        now   = datetime.now()
        user  = data.get("user", "unknown")
        sess  = data.get("sessionKey", "X")
        fname = f"{now.strftime('%Y-%m-%d_%H-%M')}_{sess}_{user}.json"
        fpath = os.path.join(hist_dir, fname)
        with open(fpath, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        subprocess.run(["git", "-C", WH_REPO, "add", "simon/gym-history/"], capture_output=True)
        msg = f"Gym: Session {sess} — {now.strftime('%Y-%m-%d')}"
        subprocess.run(["git", "-C", WH_REPO, "commit", "-m", msg], capture_output=True)
        subprocess.run(["git", "-C", WH_REPO, "push", "origin", "main"], capture_output=True)
        print(f"[gym] Committed: {fname}")
        return {"status": "committed", "file": fname}
    except Exception as e:
        print(f"[gym] commit error: {e}")
        return {"status": "error", "detail": str(e)}

@app.get("/gym/history")
async def history(request: Request, user: str = "simon"):
    auth(request)
    pattern = os.path.join(DATA_DIR, f"*_{user}.json")
    files   = sorted(glob.glob(pattern), reverse=True)[:50]
    result  = []
    for f in files:
        try:
            with open(f) as fh:
                result.append(json.load(fh))
        except Exception:
            pass
    return result

@app.get("/gym/health")
async def health():
    return {"status": "ok"}