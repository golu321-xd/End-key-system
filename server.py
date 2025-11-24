# server.py
import os, time, sqlite3, uuid
from flask import Flask, request, jsonify
from flask_cors import CORS

DB_PATH = os.getenv("DB_PATH", "db/keys.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE,
        bound_hwid TEXT,
        created_at INTEGER,
        expires_at INTEGER
    )""")
    conn.commit(); conn.close()

init_db()
app = Flask(__name__)
CORS(app)

def now_ts(): return int(time.time())
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "admin_secret_change_me")

@app.route("/create_key", methods=["POST"])
def create_key():
    token = request.headers.get("Authorization")
    if token != f"Bearer {ADMIN_TOKEN}": return jsonify({"error":"unauthorized"}),403
    data = request.json or {}
    k = data.get("key") or str(uuid.uuid4())[:8]
    expires_at = now_ts() + 24*3600
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    try:
        cur.execute("INSERT INTO keys (key, bound_hwid, created_at, expires_at) VALUES (?,?,?,?)",
                    (k, None, now_ts(), expires_at))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close(); return jsonify({"error":"key exists"}),400
    conn.close(); return jsonify({"key":k,"expires_at":expires_at})

@app.route("/bind_key", methods=["POST"])
def bind_key():
    data = request.json or {}
    key = data.get("key"); hwid = data.get("hwid")
    if not key or not hwid: return jsonify({"error":"missing"}),400
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute("SELECT bound_hwid, expires_at FROM keys WHERE key=?", (key,))
    row = cur.fetchone()
    if not row: conn.close(); return jsonify({"error":"key not found"}),404
    bound_hwid, _ = row
    if bound_hwid and bound_hwid != hwid:
        conn.close(); return jsonify({"error":"already bound"}),403
    new_expires = now_ts() + 24*3600
    cur.execute("UPDATE keys SET bound_hwid=?, expires_at=? WHERE key=?", (hwid, new_expires, key))
    conn.commit(); conn.close()
    return jsonify({"ok":True,"expires_at":new_expires})

@app.route("/validate", methods=["GET"])
def validate():
    key = request.args.get("key"); hwid = request.args.get("hwid")
    if not key or not hwid: return jsonify({"valid":False,"reason":"missing"}),400
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    cur.execute("SELECT bound_hwid, expires_at FROM keys WHERE key=?", (key,))
    row = cur.fetchone(); conn.close()
    if not row: return jsonify({"valid":False,"reason":"no_key"})
    bound_hwid, expires_at = row
    if now_ts() > (expires_at or 0): return jsonify({"valid":False,"reason":"expired"})
    if bound_hwid is None: return jsonify({"valid":False,"reason":"not_bound"})
    if bound_hwid != hwid: return jsonify({"valid":False,"reason":"hwid_mismatch"})
    return jsonify({"valid":True,"expires_at":expires_at})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
