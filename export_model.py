"""Export best MLflow run artifacts to ./model_export for Docker packaging."""
import shutil
import pathlib
import mlflow
from mlflow import MlflowClient

mlflow.set_tracking_uri("sqlite:///mlflow.db")
client = MlflowClient()

# Get the best run dynamically based on ROC-AUC
experiment_id = mlflow.get_experiment_by_name("heart-disease-classifier").experiment_id
best_runs = client.search_runs([experiment_id], order_by=["metrics.roc_auc DESC"], max_results=1)
best_run = best_runs[0]

print(f"Exporting model from run {best_run.info.run_id[:8]} (AUC: {best_run.data.metrics['roc_auc']:.4f})")

dst = pathlib.Path("model_export")
if dst.exists():
    shutil.rmtree(dst)

local_path = mlflow.artifacts.download_artifacts(
    artifact_uri=f"runs:/{best_run.info.run_id}/model", dst_path="."
)
shutil.move(local_path, dst)
print(f"Model successfully exported to {dst}/ -- contents: {[p.name for p in dst.iterdir()]}")