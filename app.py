from flask import Flask, request, jsonify
from enum import Enum
from supabase import create_client
import uuid

app = Flask(__name__)

SUPABASE_URL = "https://fejzbmttbhyhenfxnjkq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlanpibXR0Ymh5aGVuZnhuamtxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczOTk0OTczNSwiZXhwIjoyMDU1NTI1NzM1fQ.YRFeFyfN4I5Ke_LEweTwMzha2xXkLcNAyEMcwCkdfCo" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class ReasonType(Enum):
    SICK_LEAVE = "болеет"
    HOLIDAY = "праздник"
    UNKNOWN = "неизвестно"
    DAY_OFF = "отгул"

ALLOWED_REASONS = [r.value for r in ReasonType]

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "✅ Dayoff Tracker API работает!"}), 200

@app.route("/employers", methods=["POST"])
def add_employer():
    data = request.get_json()

    required = ['firstName', 'lastName', 'jobTitle']
    for field in required:
        if field not in data:
            return jsonify({"error": f"Поле '{field}' обязательно"}), 400

    data["id"] = str(uuid.uuid4())
    data.setdefault("profile_image", "")  # если не указали

    try:
        response = supabase.table("employers").insert(data).execute()
        return jsonify({"message": "Сотрудник добавлен", "id": data["id"]}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/employers", methods=["GET"])
def get_all_employers():
    try:
        response = supabase.table("employers").select("*").execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/employers/<employer_id>", methods=["GET"])
def get_employer(employer_id):
    try:
        response = (
            supabase.table("employers")
            .select("*")
            .eq("id", employer_id)
            .single()
            .execute()
        )
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": f"Сотрудник не найден: {str(e)}"}), 404

@app.route("/employers/<employer_id>", methods=["PUT"])
def update_employer(employer_id):
    data = request.get_json()

    try:
        response = (
            supabase.table("employers")
            .update(data)
            .eq("id", employer_id)
            .execute()
        )
        return jsonify({"message": "Обновлено", "data": response.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/employers/<employer_id>", methods=["DELETE"])
def delete_employer(employer_id):
    try:
        response = (
            supabase.table("employers")
            .delete()
            .eq("id", employer_id)
            .execute()
        )
        return jsonify({"message": "Удалено"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/day_offs", methods=["POST"])
def add_day_off():
    data = request.get_json()

    required = ['start_date', 'end_date', 'reason', 'employer_id']
    for field in required:
        if field not in data:
            return jsonify({"error": f"Поле '{field}' обязательно"}), 400

    if data['reason'] not in ALLOWED_REASONS:
        return jsonify({
            "error": "Недопустимая причина",
            "допустимые_причины": ALLOWED_REASONS
        }), 400

    data["id"] = str(uuid.uuid4())

    try:
        response = supabase.table("day_offs").insert(data).execute()
        return jsonify({"message": "Выходной добавлен", "data": response.data}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/day_offs/<employer_id>", methods=["GET"])
def get_day_offs(employer_id):
    try:
        result = (
            supabase.table("day_offs")
            .select("*")
            .eq("employer_id", employer_id)
            .order("start_date", desc=False)
            .execute()
        )

        if not result.data:
            return jsonify({"message": "Нет записей"}), 404

        return jsonify(result.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/day_offs/<dayoff_id>", methods=["PUT"])
def update_day_off(dayoff_id):
    data = request.get_json()
    try:
        response = (
            supabase.table("day_offs")
            .update(data)
            .eq("id", dayoff_id)
            .execute()
        )
        return jsonify({"message": "Обновлено", "data": response.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/day_offs/<dayoff_id>", methods=["DELETE"])
def delete_day_off(dayoff_id):
    try:
        response = (
            supabase.table("day_offs")
            .delete()
            .eq("id", dayoff_id)
            .execute()
        )
        return jsonify({"message": "Выходной удалён"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/sick_days/<employer_id>", methods=["GET"])
def get_sick_days(employer_id):
    try:
        result = (
            supabase.table("day_offs")
            .select("*")
            .eq("employer_id", employer_id)
            .eq("reason", "болеет")
            .order("start_date", desc=False)
            .execute()
        )
        return jsonify(result.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
