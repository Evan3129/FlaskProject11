import os
import sqlite3
import requests
from flask import Flask, jsonify, render_template, redirect, url_for, flash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_key")

API_KEY = os.getenv("THEDOG_API_KEY")
DOG_URL = "https://api.thedogapi.com/v1/images/search"
DATABASE = "dogs.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS saved_dogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_url TEXT NOT NULL,
            breed_name TEXT,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def fetch_dog_data(limit=6):
    if not API_KEY:
        return None, {
            "error": "Missing THEDOG_API_KEY. Add it to your .env file."
        }

    try:
        response = requests.get(
            DOG_URL,
            headers={"x-api-key": API_KEY},
            params={"limit": limit, "has_breeds": 1},
            timeout=5
        )

        data = response.json()

        if response.status_code != 200:
            return None, {
                "error": "Dog API error",
                "api_response": data
            }

        results = []

        for item in data:
            breed_name = "Unknown Breed"
            if item.get("breeds") and len(item["breeds"]) > 0:
                breed_name = item["breeds"][0].get("name", "Unknown Breed")

            results.append({
                "image_url": item.get("url"),
                "breed_name": breed_name
            })

        return results, None

    except requests.RequestException as e:
        return None, {
            "error": "Failed to contact dog service",
            "details": str(e)
        }


@app.route("/")
def index():
    dog_data, error = fetch_dog_data()
    return render_template("index.html", dog_data=dog_data, error=error)


@app.route("/dogs")
def dogs():
    dog_data, error = fetch_dog_data()

    if error:
        return jsonify(error), 500

    return jsonify(dog_data)


@app.route("/dogs-page")
def dogs_page():
    dog_data, error = fetch_dog_data()
    return render_template("dogs.html", dog_data=dog_data, error=error)


@app.route("/save_dogs")
def save_dogs():
    dog_data, error = fetch_dog_data()

    if error:
        flash("Could not save dog data. API key is missing or invalid.")
        return redirect(url_for("index"))

    conn = get_db_connection()

    for item in dog_data:
        conn.execute("""
            INSERT INTO saved_dogs (image_url, breed_name)
            VALUES (?, ?)
        """, (
            item["image_url"],
            item["breed_name"]
        ))

    conn.commit()
    conn.close()

    flash("Dog data saved successfully.")
    return redirect(url_for("index"))


@app.route("/saved")
def saved():
    conn = get_db_connection()
    saved_dogs = conn.execute("""
        SELECT * FROM saved_dogs
        ORDER BY saved_at DESC
    """).fetchall()
    conn.close()

    return render_template("saved.html", saved_dogs=saved_dogs)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)