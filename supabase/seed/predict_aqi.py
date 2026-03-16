from fastapi import FastAPI
import pandas as pd
import joblib
from datetime import datetime

# --------------------------------
# Initialize FastAPI
# --------------------------------
app = FastAPI(title="AQI Prediction API")

# --------------------------------
# Load trained model
# --------------------------------
try:
    model = joblib.load("aqi_model.pkl")
    print("AQI model loaded successfully")
except Exception as e:
    print("Error loading model:", e)
    model = None


# --------------------------------
# AQI Category (Indian Standard)
# --------------------------------
def get_aqi_category(aqi):
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Satisfactory"
    elif aqi <= 200:
        return "Moderate"
    elif aqi <= 300:
        return "Poor"
    elif aqi <= 400:
        return "Very Poor"
    else:
        return "Severe"


# --------------------------------
# AQI Color for UI
# --------------------------------
def get_aqi_color(aqi):
    if aqi <= 50:
        return "green"
    elif aqi <= 100:
        return "lightgreen"
    elif aqi <= 200:
        return "yellow"
    elif aqi <= 300:
        return "orange"
    elif aqi <= 400:
        return "red"
    else:
        return "maroon"


# --------------------------------
# Home Route
# --------------------------------
@app.get("/")
def home():
    return {"message": "AQI Prediction API running"}


# --------------------------------
# Prediction Route
# --------------------------------
@app.post("/predict")
def predict(data: dict):

    if model is None:
        return {"error": "Model not loaded"}

    # Convert input JSON to DataFrame
    df = pd.DataFrame([data])

    # --------------------------------
    # Time Features
    # --------------------------------
    now = datetime.now()
    df["Month_Number"] = now.month
    df["Year"] = now.year
    df["Day_of_Month"] = now.day
    df["Week_Number"] = now.isocalendar().week
    df["Quarter"] = (now.month - 1) // 3 + 1

    # --------------------------------
    # Arrange columns exactly as model expects
    # --------------------------------
    df = df[[
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
    ]]

    # --------------------------------
    # Predict AQI
    # --------------------------------
    prediction = model.predict(df)

    aqi_value = float(prediction[0])
    category = get_aqi_category(aqi_value)
    color = get_aqi_color(aqi_value)

    # --------------------------------
    # Return Response
    # --------------------------------
    return {
        "predicted_aqi": aqi_value,
        "category": category,
        "color": color
    }