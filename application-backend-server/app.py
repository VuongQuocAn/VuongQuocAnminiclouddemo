from flask import Flask, jsonify, request
import time, requests, os, json
from jose import jwt

ISSUER = os.getenv("OIDC_ISSUER", "http://authentication-identity-server:8080/realms/master")
AUDIENCE = os.getenv("OIDC_AUDIENCE", "myapp")
JWKS_URL = f"{ISSUER}/protocol/openid-connect/certs"

_JWKS = None
_TS = 0

# Đường dẫn tuyệt đối tới file dữ liệu (cùng thư mục với app.py)
STUDENTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students.json")

def get_jwks():
    global _JWKS, _TS
    now = time.time()
    if not _JWKS or now - _TS > 600:
        _JWKS = requests.get(JWKS_URL, timeout=5).json()
        _TS = now
    return _JWKS

def load_students():
    if not os.path.exists(STUDENTS_FILE):
        return []
    with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_students(data):
    with open(STUDENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

app = Flask(__name__)

# ─── CORS helper ─────────────────────────────────────────────────────────────
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@app.after_request
def after_request(response):
    return add_cors(response)

@app.route("/<path:path>", methods=["OPTIONS"])
def preflight(path):
    return add_cors(app.make_response(("", 204)))

# ─── Endpoints cũ ────────────────────────────────────────────────────────────
@app.get("/hello")
def hello():
    return jsonify(message="Hello from App Server!")

@app.get("/secure")
def secure():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify(error="Missing Bearer token"), 401
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, get_jwks(), algorithms=["RS256"],
                             audience=AUDIENCE, issuer=ISSUER)
        return jsonify(message="Secure resource OK",
                       preferred_username=payload.get("preferred_username"))
    except Exception as e:
        return jsonify(error=str(e)), 401

# ─── Student CRUD ─────────────────────────────────────────────────────────────
@app.get("/student")
def get_students():
    return jsonify(load_students())


@app.post("/student")
def create_student():
    body = request.get_json(force=True, silent=True)
    if not body:
        return jsonify(error="Request body phải là JSON"), 400

    students = load_students()
    new_id = max((s["id"] for s in students), default=0) + 1

    student = {
        "id": new_id,
        "name": body.get("name", ""),
        "mssv": body.get("mssv", ""),
        "major": body.get("major", ""),
        "gpa": body.get("gpa", 0.0)
    }
    students.append(student)
    save_students(students)
    return jsonify(student), 201


@app.put("/student/<int:student_id>")
def update_student(student_id):
    body = request.get_json(force=True, silent=True)
    if not body:
        return jsonify(error="Request body phải là JSON"), 400

    students = load_students()
    for s in students:
        if s["id"] == student_id:
            s["name"]  = body.get("name",  s["name"])
            s["mssv"]  = body.get("mssv",  s.get("mssv", ""))
            s["major"] = body.get("major", s["major"])
            s["gpa"]   = body.get("gpa",   s["gpa"])
            save_students(students)
            return jsonify(s)

    return jsonify(error=f"Sinh viên ID {student_id} không tồn tại"), 404


@app.delete("/student/<int:student_id>")
def delete_student(student_id):
    students = load_students()
    new_list = [s for s in students if s["id"] != student_id]
    if len(new_list) == len(students):
        return jsonify(error=f"Sinh viên ID {student_id} không tồn tại"), 404

    save_students(new_list)
    return jsonify(message=f"Đã xóa sinh viên ID {student_id}"), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)

