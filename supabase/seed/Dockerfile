FROM python:3.11

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir fastapi uvicorn joblib numpy pandas scikit-learn xgboost prophet google-genai python-dotenv
    
EXPOSE 8000

CMD ["uvicorn", "aqi_api:app", "--host", "0.0.0.0", "--port", "8000"]