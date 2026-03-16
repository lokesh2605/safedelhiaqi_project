# -----------------------------------------
# Train AQI Prediction Model
# -----------------------------------------

import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import joblib


# -----------------------------------------
# Load Dataset
# -----------------------------------------

df = pd.read_csv("Delhi_AQI_Main_Dataset.csv")

# Keep only numeric columns
df = df.select_dtypes(include=["number"])


# -----------------------------------------
# Define Target and Features
# -----------------------------------------

# Target variable
y = df["AQI_Value"]

# Feature variables
X = df.drop("AQI_Value", axis=1)


# -----------------------------------------
# Train / Test Split
# -----------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# -----------------------------------------
# Create XGBoost Model
# -----------------------------------------

model = XGBRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)


# -----------------------------------------
# Train Model
# -----------------------------------------

model.fit(X_train, y_train)


# -----------------------------------------
# Make Predictions
# -----------------------------------------

preds = model.predict(X_test)


# -----------------------------------------
# Model Evaluation Metrics
# -----------------------------------------

r2 = r2_score(y_test, preds)
rmse = np.sqrt(mean_squared_error(y_test, preds))
mae = mean_absolute_error(y_test, preds)
mape = np.mean(np.abs((y_test - preds) / y_test)) * 100


print("\nModel Evaluation Metrics")
print("-------------------------")
print("R² Score :", r2)
print("RMSE     :", rmse)
print("MAE      :", mae)
print("MAPE     :", mape, "%")


# -----------------------------------------
# Save Model
# -----------------------------------------

joblib.dump(model, "aqi_model.pkl")

print("\nAQI model trained and saved successfully.")