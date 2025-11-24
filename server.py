from flask import Flask, request, jsonify
import json, time, os

app = Flask(__name__)
DB_FILE = "database.json"
SECRET = os.environ.get("API_SECRET", "secret_key")

def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/setkey", methods=["POST"])
def set_key():
    if request.headers.get("Authorization") != SECRET:
        return "Unauthorized", 401

    data = request.json
    key = data.get("key")
    hwid = data.get("hwid")
    expiry = time.time() + 24*60*60

    db = load_db()
    db[key] = {"hwid": hwid, "expires": expiry}
    save_db(db)

    return {"status": "ok"}

@app.route("/verify", methods=["GET"])
def verify():
    key = request.args.get("key")
    hwid = request.args.get("hwid")

    db = load_db()
    if key not in db:
        return {"valid": False}

    entry = db[key]

    if time.time() > entry["expires"]:
        return {"valid": False, "reason": "expired"}

    if hwid != entry["hwid"]:
        return {"valid": False, "reason": "hwid_mismatch"}

    return {"valid": True}

@app.route("/")
def home():
    return "API running!"
