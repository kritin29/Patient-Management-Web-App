# backend/main.py
import os
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, auth
from pydantic import BaseModel
from typing import Optional
import requests
from datetime import datetime, timezone

load_dotenv(dotenv_path=".env")

FIREBASE_SA_PATH = os.getenv("FIREBASE_SA_PATH", "./firebase_service_account.json")
DEV_MODE = os.getenv("DEV_MODE", "true").lower() == "true"
CUSTIO_API_KEY = os.getenv("CUSTIO_API_KEY", "mock")
CUSTIO_API_URL = os.getenv("CUSTIO_API_URL", "https://api.customer.io/v1/send-mock")

# init firebase admin
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_SA_PATH)
    firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI(title="Undergrad Admin API")

# allow frontend localhost (Next dev) and others
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # narrow this in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_token(auth_header: Optional[str]):
    if DEV_MODE:
        return {"uid": "dev-admin", "email": "dev@example.com"}
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    try:
        token = auth_header.split(" ").pop()
        decoded = auth.verify_id_token(token)
        return decoded
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/api/health")
async def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

@app.get("/api/students")
async def list_students(q: Optional[str] = None, status: Optional[str] = None):
    # basic query for demo - returns list of student documents
    coll = db.collection("students")
    docs = coll.limit(100).get()
    results = []
    for d in docs:
        data = d.to_dict()
        data["id"] = d.id
        results.append(data)
    return {"students": results}

@app.get("/api/students/{sid}")
async def get_student(sid: str):
    doc = db.collection("students").document(sid).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Student not found")
    student = doc.to_dict()
    # pull subcollections: interactions, communications, notes
    interactions = [x.to_dict() for x in db.collection("students").document(sid).collection("interactions").order_by("ts", direction=firestore.Query.DESCENDING).limit(50).stream()]
    communications = [x.to_dict() for x in db.collection("students").document(sid).collection("communications").order_by("ts", direction=firestore.Query.DESCENDING).limit(50).stream()]
    notes = [x.to_dict() for x in db.collection("students").document(sid).collection("notes").order_by("ts", direction=firestore.Query.DESCENDING).limit(50).stream()]
    return {"student": student, "interactions": interactions, "communications": communications, "notes": notes}

class NoteIn(BaseModel):
    author: str
    text: str

@app.post("/api/students/{sid}/notes")
async def add_note(sid: str, note: NoteIn, authorization: Optional[str] = Header(None)):
    user = verify_token(authorization)
    note_doc = {"author": note.author, "text": note.text, "ts": firestore.SERVER_TIMESTAMP}
    col = db.collection("students").document(sid).collection("notes")
    ref = col.add(note_doc)
    return {"ok": True, "id": ref[1].id}

class CommIn(BaseModel):
    channel: str
    body: str
    logged_by: str

@app.post("/api/students/{sid}/communications")
async def add_communication(sid: str, comm: CommIn, authorization: Optional[str] = Header(None)):
    user = verify_token(authorization)
    doc = {"channel": comm.channel, "body": comm.body, "logged_by": comm.logged_by, "ts": firestore.SERVER_TIMESTAMP}
    col = db.collection("students").document(sid).collection("communications")
    ref = col.add(doc)
    return {"ok": True, "id": ref[1].id}

@app.post("/api/students/{sid}/trigger-email")
async def trigger_email(sid: str, subject: str, body: str, authorization: Optional[str] = Header(None)):
    user = verify_token(authorization)
    # Mock Customer.io call for local dev. Replace with real API call in prod.
    payload = {
        "student_id": sid,
        "subject": subject,
        "body": body,
        "triggered_by": user.get("email", "dev@example.com")
    }
    # For demo, send to CUSTIO_API_URL (can be a mock server)
    try:
        resp = requests.post(CUSTIO_API_URL, json=payload, headers={"Authorization": f"Bearer {CUSTIO_API_KEY}"})
        return {"ok": True, "status_code": resp.status_code, "response_text": resp.text}
    except Exception as e:
        return {"ok": False, "error": str(e)}
