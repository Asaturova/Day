from flask import Flask, request, jsonify
from enum import Enum
from supabase import create_client
import uuid

app = Flask(__name__)

# 🔐 Твои ключи Supabase
SUPABASE_URL = "https://fejzbmttbhyhenfxnjkq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # укоротила для безопасности
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 📚 Enum — причины отсутствия
class ReasonType(Enum):
    SICK_LEAVE = "болеет"
    HOLIDAY = "праздник"
    UNKNOWN = "неизвестно"
    DAY_OFF = "отгул"

ALLOWED_REASONS = [r.value for r in ReasonType]

# ===================== EMPLOYERS =====================

# ➕ Добавить сотрудника
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

# 📄 Получить всех сотрудников
@app.route("/employers", methods=["GET"])
def get_all_employers():
    try:
        response = supabase.table("employers").select("*").execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 👤 Получить одного сотрудника
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

# ✏️ Обновить сотрудника
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

# ❌ Удалить сотрудника
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

# ===================== DAY OFFS =====================

# ➕ Добавить выходной
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

# 📄 Получить выходные по сотруднику
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

# ✏️ Обновить выходной
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

# ❌ Удалить выходной
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

# ===================== СТАРТ СЕРВЕРА =====================

if __name__ == "__main__":
    app.run(debug=True)