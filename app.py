from flask import Flask, request, jsonify
from enum import Enum
from supabase import create_client
import uuid
from datetime import datetime

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
def home():
    return jsonify({"message": "Dayoff Tracker API работает 💡"}), 200

@app.route("/employers", methods=["POST"])
def add_employer():
    data = request.get_json()

    required = ['firstName', 'lastName', 'jobTitle']
    for field in required:
        if field not in data:
            return jsonify({"error": f"Поле '{field}' обязательно"}), 400

    data["id"] = str(uuid.uuid4())
    data.setdefault("profile_image", "")  
    data["vacation_limit"] = 30

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
    
@app.route("/vacations", methods=["POST"])
def add_vacation():
    data = request.get_json()

    required = ['start_date', 'end_date', 'employer_id']
    for field in required:
        if field not in data:
            return jsonify({"error": f"Поле '{field}' обязательно"}), 400

    data["id"] = str(uuid.uuid4())

    try:
        response = supabase.table("vacations").insert(data).execute()
        return jsonify({"message": "Отпуск добавлен", "data": response.data}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/vacations/<employer_id>", methods=["GET"])
def get_vacations_by_employer(employer_id):
    try:
        result = (
            supabase.table("vacations")
            .select("*")
            .eq("employer_id", employer_id)
            .order("start_date", desc=False)
            .execute()
        )
        return jsonify(result.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/vacation/<vacation_id>", methods=["PUT"])
def update_vacation(vacation_id):
    data = request.get_json()
    try:
        response = (
            supabase.table("vacations")
            .update(data)
            .eq("id", vacation_id)
            .execute()
        )
        return jsonify({"message": "Отпуск обновлён", "data": response.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/vacation/<vacation_id>", methods=["DELETE"])
def delete_vacation(vacation_id):
    try:
        response = (
            supabase.table("vacations")
            .delete()
            .eq("id", vacation_id)
            .execute()
        )
        return jsonify({"message": "Отпуск удалён"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/vacation-balances", methods=["GET"])
def vacation_balances():
    try:
        employers = supabase.table("employers").select("id, firstName, lastName, vacation_limit").execute().data
        balances = []

        for emp in employers:
            emp_id = emp["id"]
            full_name = f"{emp['firstName']} {emp['lastName']}"
            limit = emp.get("vacation_limit", 30)

            vacations = supabase.table("vacations").select("start_date, end_date").eq("employer_id", emp_id).execute().data

            used_days = 0
            for v in vacations:
                start = datetime.fromisoformat(v["start_date"])
                end = datetime.fromisoformat(v["end_date"])
                used_days += (end - start).days + 1

            remaining = max(0, limit - used_days)

            balances.append({
                "name": full_name,
                "used_days": used_days,
                "remaining_days": remaining
            })

        return jsonify(balances), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/vacation-balance/<employer_id>", methods=["GET"])
def vacation_balance_single(employer_id):
    try:
        emp = supabase.table("employers").select("firstName, lastName, vacation_limit").eq("id", employer_id).single().execute().data
        full_name = f"{emp['firstName']} {emp['lastName']}"
        limit = emp.get("vacation_limit", 30)

        vacations = supabase.table("vacations").select("start_date, end_date").eq("employer_id", employer_id).execute().data

        used_days = sum((datetime.fromisoformat(v["end_date"]) - datetime.fromisoformat(v["start_date"])).days + 1 for v in vacations)
        remaining = max(0, limit - used_days)

        return jsonify({"name": full_name, "used_days": used_days, "remaining_days": remaining}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/missed_days", methods=["POST"])
def post_total_missed_days():
    data = request.get_json()

    if "employer_id" not in data:
        return jsonify({"error": "Поле 'employer_id' обязательно"}), 400

    try:
        days = supabase.table("day_offs").select("start_date, end_date").eq("employer_id", data["employer_id"]).execute().data

        total = 0
        for d in days:
            start = datetime.fromisoformat(d["start_date"])
            end = datetime.fromisoformat(d["end_date"])
            total += (end - start).days + 1

        return jsonify({"missed_days": total}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
