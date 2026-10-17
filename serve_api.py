import os
import logging
import mlflow.pyfunc
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator

# 1. Configure standard logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("heart-disease-api")

state = {}
MODEL_PATH = os.getenv("MODEL_PATH")

@asynccontextmanager
async def lifespan(app: FastAPI):
    if MODEL_PATH:
        logger.info(f"Loading scikit-learn model from environment MODEL_PATH: {MODEL_PATH}")
        state["model"] = mlflow.sklearn.load_model(MODEL_PATH)
    else:
        logger.info("No MODEL_PATH set. Falling back to local SQLite MLflow registry...")
        mlflow.set_tracking_uri("sqlite:///mlflow.db")
        experiment_id = mlflow.get_experiment_by_name("heart-disease-classifier").experiment_id
        best_run = mlflow.search_runs(experiment_id, order_by=["metrics.roc_auc DESC"], max_results=1).iloc[0]
        state["model"] = mlflow.sklearn.load_model(f"runs:/{best_run.run_id}/model")
    
    yield
    state.clear()

app = FastAPI(title="Heart Disease API", lifespan=lifespan)

# 2. Instrument the FastAPI app for Prometheus metrics
Instrumentator().instrument(app).expose(app)

class Patient(BaseModel):
    age: int = Field(ge=0, le=120)
    sex: int = Field(ge=0, le=1)
    cp: int = Field(ge=1, le=4)
    trestbps: float = Field(ge=0)
    chol: float = Field(ge=0)
    fbs: int = Field(ge=0, le=1)
    restecg: int = Field(ge=0, le=2)
    thalach: float = Field(ge=0)
    exang: int = Field(ge=0, le=1)
    oldpeak: float
    slope: int = Field(ge=1, le=3)
    ca: float = Field(ge=0, le=3)
    thal: float = Field(ge=3, le=7)

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": "model" in state}

@app.post("/predict")
def predict(patient: Patient):
    df = pd.DataFrame([patient.model_dump()])
    pred = int(state["model"].predict(df)[0])
    
    try:
        confidence = float(state["model"].predict_proba(df)[0][1])
    except AttributeError:
        confidence = 0.0 

    risk_status = "High Risk" if pred == 1 else "Low Risk"

    # 3. Log the incoming request and the resulting prediction
    logger.info(f"Prediction: {risk_status} (Confidence: {confidence:.4f}) | Payload: {patient.model_dump()}")

    return {
        "prediction": pred,
        "confidence": round(confidence, 4),
        "risk_status": risk_status
    }