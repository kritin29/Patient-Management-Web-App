# backend/seed_students.py
import os
import random
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Load .env
load_dotenv(".env")

# --- Set Firestore emulator host BEFORE initializing Firebase ---
emulator_host = os.getenv("FIRESTORE_EMULATOR_HOST", "127.0.0.1:9099")
os.environ["FIRESTORE_EMULATOR_HOST"] = emulator_host

# --- Initialize Firebase Admin SDK ---
sa_path = os.getenv("FIREBASE_SA_PATH", "./firebase_service_account.json")
cred = credentials.Certificate(sa_path)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
print("Firebase Admin initialized. Using Firestore emulator at:", emulator_host)

# --- Seed function ---
def seed(n=25):
    statuses = ["Exploring", "Shortlisting", "Applying", "Submitted"]
    countries = ["IN", "US", "CA", "AE", "UK"]

    for i in range(n):
        doc = {
            "name": f"Student {i+1}",
            "email": f"student{i+1}@example.com",
            "phone": f"+91-90000{i:04d}",
            "grade": random.choice([11, 12]),
            "country": random.choice(countries),
            "application_status": random.choice(statuses),
            "last_active": (datetime.now(timezone.utc) - timedelta(days=random.randint(0,30))).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tags": ["high_intent"] if i % 5 == 0 else []
        }

        # Add student document
        ref = db.collection("students").add(doc)
        sid = ref[1].id

        # Add subcollections
        db.collection("students").document(sid).collection("interactions").add({
            "type": "login",
            "ts": datetime.now(timezone.utc).isoformat(),
            "details": "Logged in (seed)"
        })
        db.collection("students").document(sid).collection("notes").add({
            "author": "system",
            "text": "Seed note",
            "ts": datetime.now(timezone.utc).isoformat()
        })

    print("Seeded", n, "students.")

# --- Run seeding ---
if __name__ == "__main__":
    seed(30)

    # List top-level collections to confirm
    collections = [c.id for c in db.collections()]
    print("Top-level collections in Firestore emulator:", collections)
