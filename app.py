import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# -----------------------
# CONFIG FROM ENV VARS
# -----------------------
API_KEY = os.getenv("OPENWEATHER_API_KEY")   # comes from .env
CITY = os.getenv("CITY", "Cork")             # default Cork if not provided
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


@app.route("/")
def index():
    return weather()


@app.route("/weather")
def weather():
    # helpful error if the key isn't set
    if not API_KEY:
        return jsonify({
            "error": "Missing OPENWEATHER_API_KEY. Add it to your .env file or pass it as an environment variable."
        }), 500

    try:
        r = requests.get(
            WEATHER_URL,
            params={"q": CITY, "appid": API_KEY, "units": "metric"},
            timeout=5
        )

        data = r.json()

        if r.status_code != 200:
            return jsonify({
                "error": "Weather API error",
                "api_response": data
            }), 502

        return jsonify({
            "city": CITY,
            "temperature": data["main"]["temp"],
            "conditions": data["weather"][0]["description"]
        })

    except requests.RequestException as e:
        return jsonify({
            "error": "Failed to contact weather service",
            "details": str(e)
        }), 503


if __name__ == "__main__":
    # IMPORTANT for Docker
    app.run(host="0.0.0.0", port=5000, debug=True)