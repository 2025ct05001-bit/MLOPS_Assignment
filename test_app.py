"""Pytest suite for data processing and model API."""
import pytest
from fastapi.testclient import TestClient
from serve_api import app

def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["model_loaded"] is True

def test_predict_endpoint_validation():
    with TestClient(app) as client:
        # Missing parameters should throw a 422 Unprocessable Entity
        bad_payload = {"age": 45} 
        response = client.post("/predict", json=bad_payload)
        assert response.status_code == 422

def test_predict_endpoint_valid():
    with TestClient(app) as client:
        valid_payload = {
            "age": 52,
            "sex": 1,
            "cp": 1,
            "trestbps": 125,
            "chol": 212,
            "fbs": 0,
            "restecg": 1,
            "thalach": 168,
            "exang": 0,
            "oldpeak": 1.0,
            "slope": 2,
            "ca": 2,
            "thal": 3
        }
        response = client.post("/predict", json=valid_payload)
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "confidence" in data