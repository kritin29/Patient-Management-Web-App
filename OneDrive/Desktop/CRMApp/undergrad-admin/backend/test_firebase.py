import os
from firebase_admin import credentials, initialize_app, firestore
from dotenv import load_dotenv

load_dotenv(".env")

path = os.getenv("FIREBASE_SA_PATH", "./firebase_service_account.json")
print("Using service account path:", path)

cred = credentials.Certificate(path)
initialize_app(cred)

# Tell Firestore client to use emulator if set
emulator_host = os.getenv("FIRESTORE_EMULATOR_HOST")
if emulator_host:
    os.environ["FIRESTORE_EMULATOR_HOST"] = emulator_host

db = firestore.client()
print("Firebase admin initialized. Firestore client ready.")

# List top-level collections
print("Collections:", [c.id for c in db.collections()])
