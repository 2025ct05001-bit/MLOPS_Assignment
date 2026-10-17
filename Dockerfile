# ... (Previous Dockerfile steps) ...
FROM python:3.11-slim
ENV MODEL_PATH=/app/model_export
WORKDIR /app

# Copy and install exact requirements for reproducibility
COPY model_export/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt fastapi "uvicorn[standard]" pydantic prometheus-fastapi-instrumentator

# Copy model artifacts and application code into the image
COPY model_export/ /app/model_export/
COPY serve_api.py .

EXPOSE 8000

# Run Uvicorn server inside the container
CMD ["python", "-m", "uvicorn", "serve_api:app", "--host", "0.0.0.0", "--port", "8000"]
