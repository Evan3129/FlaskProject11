import os
import time
import uuid
import logging
import requests
import psycopg
from flask import Flask, jsonify, render_template, redirect, url_for, flash, request, g
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_key")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

API_KEY = os.getenv("THEDOG_API_KEY")
DOG_URL = "https://api.thedogapi.com/v1/images/search?has_breeds=1"
DATABASE_URL = os.getenv("DATABASE_URL")

@app.before_request
def start_timer():
    g.start = time.time()
    g.request_id = str(uuid.uuid4())[:8]
    logger.info(f"request_id={g.request_id} method={request.method} path={request.path}")

@app.after_request
def log_request(response):
    duration = round((time.time() - g.start) * 1000, 2)
    logger.info(f"request_id={g.request_id} status={response.status_code} duration={duration}ms")
    return response

def get_db_connection():
    return psycopg.connect(DATABASE_URL)


def init_db():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS saved_dogs (
                id SERIAL PRIMARY KEY,
                image_url TEXT NOT NULL,
                breed_name TEXT,
                breed_group TEXT,
                origin TEXT,
                temperament TEXT,
                life_span TEXT,
                height TEXT,
                weight TEXT,
                description TEXT,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def fetch_dog_data(limit=6):
    if not API_KEY:
        return None, {"error": "Missing THEDOG_API_KEY. Add it to your .env file."}

    retries = 3
    for attempt in range(retries):
        try:
            breeds_response = requests.get(
                "https://api.thedogapi.com/v1/breeds",
                headers={"x-api-key": API_KEY},
                timeout=5
            )
            breeds_data = breeds_response.json()

            import random
            selected = random.sample(breeds_data, min(limit, len(breeds_data)))

            results = []
            for breed in selected:
                image_url = None
                if breed.get("image") and breed["image"].get("url"):
                    image_url = breed["image"]["url"]

                if image_url:
                    results.append({
                        "image_url": image_url,
                        "breed_name": breed["name"],
                        "breed_group": breed.get("breed_group", "Unknown"),
                        "origin": breed.get("origin", "Unknown"),
                        "temperament": breed.get("temperament", "Unknown"),
                        "life_span": breed.get("life_span", "Unknown"),
                        "description": breed.get("description", ""),
                        "height": breed.get("height", {}).get("metric", "Unknown"),
                        "weight": breed.get("weight", {}).get("metric", "Unknown"),
                    })

            return results, None

        except requests.RequestException as e:
            wait = 2 ** attempt
            logger.warning(f"API attempt {attempt + 1} failed: {e}. Retrying in {wait}s...")
            time.sleep(wait)

    return None, {"error": "Failed to contact dog service after retries", "details": "Max retries exceeded"}




@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/status")
def status():
    status_data = {
        "app": "running",
        "database": "unknown",
        "api": "unknown"
    }

    try:
        with get_db_connection() as conn:
            conn.execute("SELECT 1")
        status_data["database"] = "connected"
    except Exception as e:
        status_data["database"] = f"error: {str(e)}"

    try:
        response = requests.get(
            "https://api.thedogapi.com/v1/breeds",
            headers={"x-api-key": API_KEY},
            timeout=5
        )
        if response.status_code == 200:
            status_data["api"] = "reachable"
        else:
            status_data["api"] = f"error: {response.status_code}"
    except Exception as e:
        status_data["api"] = f"error: {str(e)}"

    return jsonify(status_data), 200


@app.route("/test_breeds")
def test_breeds():
    response = requests.get(
        "https://api.thedogapi.com/v1/breeds",
        headers={"x-api-key": API_KEY},
        timeout=5
    )
    return jsonify(response.json()[:2])


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dogs")
def dogs():
    dog_data, error = fetch_dog_data()

    if error:
        return jsonify(error), 500

    return jsonify(dog_data)


@app.route("/search")
def search():
    query = request.args.get("q", "").lower()

    try:
        breeds_response = requests.get(
            "https://api.thedogapi.com/v1/breeds",
            headers={"x-api-key": API_KEY},
            timeout=5
        )
        breeds_data = breeds_response.json()

        results = []
        for breed in breeds_data:
            if query in breed["name"].lower():
                image_url = None
                if breed.get("image") and breed["image"].get("url"):
                    image_url = breed["image"]["url"]
                if image_url:
                    results.append({
                        "image_url": image_url,
                        "breed_name": breed["name"],
                        "breed_group": breed.get("breed_group", "Unknown"),
                        "origin": breed.get("origin", "Unknown"),
                        "temperament": breed.get("temperament", "Unknown"),
                        "life_span": breed.get("life_span", "Unknown"),
                        "description": breed.get("description", ""),
                        "height": breed.get("height", {}).get("metric", "Unknown"),
                        "weight": breed.get("weight", {}).get("metric", "Unknown"),
                    })

        return render_template("dogs.html", dog_data=results, error=None, query=query)

    except requests.RequestException as e:
        return render_template("dogs.html", dog_data=None, error={"error": str(e)}, query=query)


@app.route("/dogs-page")
def dogs_page():
    dog_data, error = fetch_dog_data()
    return render_template("dogs.html", dog_data=dog_data, error=error)


@app.route("/save_dog", methods=["POST"])
def save_dog():
    image_url = request.form.get("image_url")
    breed_name = request.form.get("breed_name")
    breed_group = request.form.get("breed_group")
    origin = request.form.get("origin")
    temperament = request.form.get("temperament")
    life_span = request.form.get("life_span")
    height = request.form.get("height")
    weight = request.form.get("weight")
    description = request.form.get("description")

    if not image_url or not breed_name:
        flash("Missing dog data.")
        return redirect(request.referrer or url_for("dogs_page"))

    with get_db_connection() as conn:
        conn.execute("""
            INSERT INTO saved_dogs (image_url, breed_name, breed_group, origin, temperament, life_span, height, weight, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (image_url, breed_name, breed_group, origin, temperament, life_span, height, weight, description))
        conn.commit()

    flash(f"{breed_name} saved successfully!")
    return redirect(request.referrer or url_for("dogs_page"))


@app.route("/saved")
def saved():
    with get_db_connection() as conn:
        rows = conn.execute("""
            SELECT id, image_url, breed_name, breed_group, origin, temperament, life_span, height, weight, description
            FROM saved_dogs
            ORDER BY saved_at DESC
        """).fetchall()

    saved_dogs = [
        {
            "id": row[0],
            "image_url": row[1],
            "breed_name": row[2],
            "breed_group": row[3],
            "origin": row[4],
            "temperament": row[5],
            "life_span": row[6],
            "height": row[7],
            "weight": row[8],
            "description": row[9]
        }
        for row in rows
    ]

    return render_template("saved.html", saved_dogs=saved_dogs)


@app.route("/delete_dog/<int:dog_id>")
def delete_dog(dog_id):
    with get_db_connection() as conn:
        conn.execute("DELETE FROM saved_dogs WHERE id = %s", (dog_id,))
        conn.commit()
    flash("Dog deleted successfully.")
    return redirect(url_for("saved"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)