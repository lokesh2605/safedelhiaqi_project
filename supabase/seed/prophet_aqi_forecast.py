import pandas as pd
from prophet import Prophet

# -----------------------------
# Load dataset
# -----------------------------
df = pd.read_csv("Delhi_AQI_Main_Dataset.csv")

# -----------------------------
# Prepare data for Prophet
# Prophet requires columns: ds, y
# -----------------------------
data = df[["Date", "AQI_Value"]].copy()

data["Date"] = pd.to_datetime(data["Date"])

data.columns = ["ds", "y"]

# -----------------------------
# Create Prophet model
# -----------------------------
model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False
)

# Train model
model.fit(data)

# -----------------------------
# Predict next 5 years
# -----------------------------
future = model.make_future_dataframe(periods=365*5)

forecast = model.predict(future)

# -----------------------------
# Save forecast
# -----------------------------
forecast[["ds","yhat","yhat_lower","yhat_upper"]].to_csv(
    "aqi_5year_forecast.csv", index=False
)

print("✅ 5-Year AQI Forecast Generated")