import json
import os
import random
import string
from flask import Flask, request, jsonify

# --- НАСТРОЙКИ ---
DB_FILE = "database.json"
SECRET_SALT = "Boom_Xt_Super_Secret_Key_2026"  # Секретное слово (никому не показывай)

app = Flask(__name__)


def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)


# --- ГЕНЕРАТОР КЛЮЧЕЙ ---
def generate_keys(count=1):
    db = load_db()
    new_keys = []
    for _ in range(count):
        # Генерируем ключ вида BOOM-XXXX-XXXX
        part1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        key = f"BOOM-{part1}-{part2}"

        # Сохраняем ключ в базу как "свободный"
        db[key] = {
            "status": "free",
            "hwid": None
        }
        new_keys.append(key)

    save_db(db)
    return new_keys


# --- API ДЛЯ ПРОГРАММЫ ---
@app.route('/check_key', methods=['POST'])
def check_key():
    data = request.json
    key = data.get('key')
    hwid = data.get('hwid')

    if not key or not hwid:
        return jsonify({"status": "error", "message": "Нет ключа или HWID"}), 400

    db = load_db()

    if key not in db:
        return jsonify({"status": "error", "message": "Ключ не найден"}), 403

    key_info = db[key]

    # Если ключ свободен — привязываем к HWID
    if key_info["status"] == "free":
        key_info["status"] = "activated"
        key_info["hwid"] = hwid
        save_db(db)
        return jsonify({"status": "success", "message": "Ключ активирован!"})

    # Если ключ уже активирован
    elif key_info["status"] == "activated":
        if key_info["hwid"] == hwid:
            return jsonify({"status": "success", "message": "Добро пожаловать!"})
        else:
            return jsonify({"status": "error", "message": "Ключ уже привязан к другому ПК"}), 403

    return jsonify({"status": "error", "message": "Неизвестная ошибка"}), 500


if __name__ == "__main__":
    # При запуске сервера он спросит, сколько ключей сгенерировать
    print("--- ГЕНЕРАТОР КЛЮЧЕЙ ---")
    count = input("Сколько ключей создать? (нажми Enter для 1): ")
    if not count.strip():
        count = 1

    try:
        keys = generate_keys(int(count))
        print(f"\nСоздано {len(keys)} ключей:")
        for k in keys:
            print(k)
        print("\nКлючи сохранены в database.json")
    except ValueError:
        print("Ошибка: введи число")

    print("\n--- ЗАПУСК СЕРВЕРА ---")
    app.run(host='0.0.0.0', port=5000)