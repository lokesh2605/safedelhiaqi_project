from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import joblib
from datetime import datetime, timedelta
import os
from google import genai
from dotenv import load_dotenv

# --------------------------------
# Gemini AI Configuration
# --------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print("Gemini key loaded:", bool(GEMINI_API_KEY))

client = None

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
    print("Gemini AI client initialized")
else:
    print("Warning: GEMINI_API_KEY not set. AI advisor disabled.")

# --------------------------------
# Initialize FastAPI
# --------------------------------

app = FastAPI(title="SafeDelhiAQI API")

# --------------------------------
# Enable CORS
# --------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:8081",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------
# Load AQI ML Model
# --------------------------------

try:
    model = joblib.load("aqi_model.pkl")
    print("AQI model loaded successfully")
except Exception as e:
    print("Error loading model:", e)
    model = None

# --------------------------------
# AQI Category Function
# --------------------------------

def get_aqi_category(aqi):

    if aqi <= 50:
        return "Good", "green"
    elif aqi <= 100:
        return "Satisfactory", "lightgreen"
    elif aqi <= 200:
        return "Moderate", "yellow"
    elif aqi <= 300:
        return "Poor", "orange"
    elif aqi <= 400:
        return "Very Poor", "red"
    else:
        return "Severe", "purple"

# --------------------------------
# Feature Preparation
# --------------------------------

def prepare_features(data, date):

    df = pd.DataFrame([data])

    # -------------------------------------------------
    # FIX: Ensure pollutant columns always exist
    # Frontend does not send them currently
    # so we create default realistic values
    # -------------------------------------------------

    df["PM2.5_µgm³"] = data.get("pm2_5", 60)
    df["PM10_µgm³"] = data.get("pm10", 120)
    df["NO₂_µgm³"] = data.get("no2", 40)
    df["SO₂_µgm³"] = data.get("so2", 10)
    df["CO_mgm³"] = data.get("co", 1)

    # --------------------------------
    # Time Features
    # --------------------------------

    df["Month_Number"] = date.month
    df["Year"] = date.year
    df["Day_of_Month"] = date.day
    df["Week_Number"] = int(date.isocalendar().week)
    df["Quarter"] = (date.month - 1) // 3 + 1

    # --------------------------------
    # Weather Features
    # --------------------------------

    df["Temperature_C"] = data.get("temperature", 25)
    df["Humidity_%"] = data.get("humidity", 60)
    df["Wind_Speed_ms"] = data.get("wind_speed", 2)
    df["Wind_Direction_deg"] = data.get("wind_direction", 180)
    df["Rainfall_mm"] = data.get("rainfall", 0)
    df["Atmospheric_Pressure_hPa"] = data.get("pressure", 1013)
    df["Visibility_km"] = data.get("visibility", 10)

    # --------------------------------
    # Additional Pollutants
    # --------------------------------

    df["O₃_µgm³"] = data.get("o3", 20)
    df["NH₃_µgm³"] = data.get("nh3", 10)

    df["Is_Festival"] = 0

    # --------------------------------
    # Arrange columns exactly as model expects
    # --------------------------------

    df = df[
        [
            "Month_Number",
            "Year",
            "Day_of_Month",
            "PM2.5_µgm³",
            "PM10_µgm³",
            "NO₂_µgm³",
            "SO₂_µgm³",
            "CO_mgm³",
            "O₃_µgm³",
            "NH₃_µgm³",
            "Temperature_C",
            "Humidity_%",
            "Wind_Speed_ms",
            "Wind_Direction_deg",
            "Rainfall_mm",
            "Atmospheric_Pressure_hPa",
            "Visibility_km",
            "Is_Festival",
            "Week_Number",
            "Quarter"
        ]
    ]

    return df.astype(float)

# --------------------------------
# Health Routes
# --------------------------------

@app.get("/")
def home():
    return {"message": "SafeDelhiAQI API running"}

@app.get("/health")
def health():
    return {"status": "ok"}

# --------------------------------
# AQI Prediction
# --------------------------------

@app.post("/predict")
def predict(data: dict):

    if model is None:
        return {"error": "Model not loaded"}

    try:

        now = datetime.now()

        df = prepare_features(data, now)

        prediction = model.predict(df)

        aqi = float(prediction[0])

        category, color = get_aqi_category(aqi)

        return {
            "predicted_aqi": aqi,
            "category": category,
            "color": color
        }

    except Exception as e:
        return {"error": str(e)}

# --------------------------------
# 7 Day Forecast
# --------------------------------

@app.post("/forecast")
def forecast(data: dict):

    if model is None:
        return {"error": "Model not loaded"}

    try:

        results = []
        now = datetime.now()

        for i in range(7):

            future_date = now + timedelta(days=i)

            df = prepare_features(data, future_date)

            prediction = model.predict(df)

            aqi = float(prediction[0])

            category, color = get_aqi_category(aqi)

            results.append({
                "day": i + 1,
                "date": future_date.strftime("%Y-%m-%d"),
                "predicted_aqi": aqi,
                "category": category,
                "color": color
            })

        return {"forecast": results}

    except Exception as e:
        return {"error": str(e)}

# --------------------------------
# 10 Year Forecast
# --------------------------------

@app.post("/forecast-long")
def forecast_long(data: dict):

    if model is None:
        return {"error": "Model not loaded"}

    try:

        results = []
        current_year = datetime.now().year

        for i in range(10):

            future_year = current_year + i

            future_date = datetime(future_year, 1, 1)

            df = prepare_features(data, future_date)

            prediction = model.predict(df)

            aqi = float(prediction[0])

            category, color = get_aqi_category(aqi)

            results.append({
                "year": future_year,
                "predicted_aqi": aqi,
                "category": category,
                "color": color
            })

        return {"forecast": results}

    except Exception as e:
        return {"error": str(e)}

# --------------------------------
# 5 Year Forecast (Prophet CSV)
# --------------------------------

@app.get("/forecast-5years")
def forecast_5years():

    try:

        df = pd.read_csv("aqi_5year_forecast.csv")

        results = []

        for i in range(0, len(df), 365):

            row = df.iloc[i]

            results.append({
                "date": row["ds"],
                "predicted_aqi": float(row["yhat"])
            })

        return {"forecast": results}

    except Exception as e:
        return {"error": str(e)}

# --------------------------------
# AI AQI Health Advisor
# --------------------------------
@app.post("/aqi-advice")
def aqi_advice(data: dict):

    aqi = data.get("aqi", 150)

    # Fallback advice (used if Gemini fails)
    if aqi <= 50:
        fallback = "Air quality is good. Outdoor activities are safe."
    elif aqi <= 100:
        fallback = "Air quality is satisfactory. Sensitive people should limit long outdoor exposure."
    elif aqi <= 200:
        fallback = "Moderate pollution. People with asthma should reduce outdoor exertion."
    elif aqi <= 300:
        fallback = "Poor air quality. Wear a mask and limit outdoor activity."
    elif aqi <= 400:
        fallback = "Very poor air quality. Avoid outdoor activity and use air purifiers indoors."
    else:
        fallback = "Severe air pollution. Stay indoors and wear N95 masks if going outside."

    if client is None:
        return {"aqi": aqi, "advice": fallback}

    try:

        prompt = f"""
AQI level is {aqi}.
Give short health advice including:
- outdoor safety
- mask recommendation
- travel advice
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        return {
            "aqi": aqi,
            "advice": response.text
        }

    except Exception as e:

        # If Gemini fails, return fallback
        return {
            "aqi": aqi,
            "advice": fallback,
            "source": "fallback",
            "error": str(e)
        }