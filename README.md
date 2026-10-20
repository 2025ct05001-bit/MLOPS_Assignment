# End-to-End MLOps Pipeline: Heart Disease Prediction

This repository contains a complete Machine Learning Operations (MLOps) pipeline for predicting heart disease. It demonstrates the transition of a machine learning model from exploratory data analysis (EDA) and experimental tracking into a highly available, monitored local production environment using a decoupled microservices architecture.

## Architecture Overview

* **Data Processing & EDA:** Python, Pandas, Seaborn/Matplotlib.
* **Model Training & Tracking:** Python, Scikit-Learn, MLflow (SQLite backend).
* **Model Serving:** FastAPI, Uvicorn, Pydantic.
* **Containerization:** Docker (`python:3.11-slim`).
* **CI/CD Orchestration:** Jenkins (Host-native declarative pipeline).
* **Deployment:** Kubernetes (Minikube), Helm.
* **Observability:** Prometheus, Grafana, `prometheus-fastapi-instrumentator`.

## Prerequisites

Ensure the following tools are installed and running on your local workstation:

* **Docker Engine** (Running)
* **Minikube & kubectl**
* **Helm**
* **Jenkins** (Installed natively on the host, not containerized)
* **Python 3.11+**

## Step 1: Environment Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/2025ct05001-bit/MLOPS_Assignment.git](https://github.com/2025ct05001-bit/MLOPS_Assignment.git)
   cd MLOPS_Assignment
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Exploratory Data Analysis (EDA)

Before training, the raw clinical dataset must be cleaned and visualized.

1. **Execute the EDA script:**
   ```bash
   python 1_eda.py

## Step 3: Model Training & Experiment Tracking

1. **Run parameterized model training:**
   The training script logs hyperparameters, metrics (Accuracy, F1, Recall, Precision, AUC), and model artifacts to a local SQLite database via MLflow. Execute the following commands to train and compare different models:
   ```bash
   python 2_train_tracked.py --model logreg
   python 2_train_tracked.py --model rf -C 0.5 --n-estimators 10
   python 2_train_tracked.py --model rf -C 0.2 --n-estimators 30
   ```

2. **View the MLflow Model Registry:**
   Launch the MLflow UI, pointing it to the SQLite backend:
   ```bash
   mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5001
   ```
   Access the dashboard in your browser at: http://localhost:5001

   *(Troubleshooting: If MLflow throws a "Malformed experiment" error from old cache files, stop the server, run `rm -rf mlruns mlflow.db`, re-run the training scripts, and start the UI again).*

## Step 4: Local API Validation

Before deploying, ensure the FastAPI application and model artifacts function correctly.

1. **Run the Unit Tests:**
   ```bash
   pytest test_app.py
   ```
   This validates the Pydantic schema constraints and endpoint health.

2. **Test the API locally (Optional):**
   ```bash
   uvicorn serve_api:app --host 0.0.0.0 --port 8000
   ```
   Access the interactive Swagger UI at: http://localhost:8000/docs

## Step 5: Kubernetes Cluster & Routing Setup

1. **Initialize Minikube and enable the Ingress controller:**
   ```bash
   minikube start
   minikube addons enable ingress
   ```

2. **Configure Local DNS:**
   Map the local application domains to your localhost. Open your `/etc/hosts` file (requires sudo) and append the following line:
   ```text
   127.0.0.1 heart-disease-api.local grafana.local
   ```

3. **Establish the Minikube Tunnel:**
   In a dedicated terminal window, run the tunnel command and leave it open so the Ingress controller can route external traffic into the cluster:
   ```bash
   minikube tunnel
   ```

## Step 6: CI/CD Pipeline Execution (Jenkins)

1. **Start the Jenkins Server:**
   Ensure Jenkins is running natively on your host machine to inherit your PATH variables.
   ```bash
   jenkins-lts
   ```

2. **Configure and Run the Pipeline:**
   * Open Jenkins (http://localhost:8080).
   * Create a new "Pipeline" job and point it to the `Jenkinsfile` in this repository.
   * Click **Build Now**.

   The pipeline will automatically execute the following stages:
   * **Unit Testing (CI):** Spins up a temporary Python container to run pytest.
   * **Build Docker Image:** Executes `docker build -t heart-disease-api:${BUILD_NUMBER}`.
   * **Push to Minikube Cache:** Executes `minikube image load` to bypass external Docker registries.
   * **Deploy to Kubernetes (CD):** Executes a zero-downtime helm upgrade against the `heart-disease` namespace natively (agent any).

## Step 7: Observability & Monitoring

1. **Deploy the Monitoring Stack (if not already installed):**
   ```bash
   helm repo add prometheus-community [https://prometheus-community.github.io/helm-charts](https://prometheus-community.github.io/helm-charts)
   helm repo update
   helm install metrics-stack prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
   ```

2. **Apply the ServiceMonitor:**
   Link Prometheus to the FastAPI application by applying the custom ServiceMonitor. This instructs Prometheus to scrape port 8000 on any pod matching the Helm release labels:
   ```bash
   kubectl apply -f monitor.yaml
   ```

3. **View Live API Metrics:**
   Navigate to http://grafana.local in your browser. You can query the FastAPI metrics dynamically using PromQL.

   Example Queries:
   * **Total API Traffic:** `http_requests_total`
   * **95th Percentile Latency:** `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, handler))`

## Step 8: Making a Prediction

Once deployed, you can send clinical data to your Kubernetes-hosted API to get a heart disease prediction.

Run the following cURL command in your terminal:

```bash
curl -X 'POST' \
  '[http://heart-disease-api.local/predict](http://heart-disease-api.local/predict)' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "age": 52,
  "sex": 1,
  "cp": 4,
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
}'
```