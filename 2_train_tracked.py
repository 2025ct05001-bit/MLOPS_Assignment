"""Train models with MLflow tracking and register the best one."""
import argparse
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score

TRACKING_URI = "sqlite:///mlflow.db"
EXPERIMENT = "heart-disease-classifier"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=["logreg", "rf"], required=True)
    ap.add_argument("--C", type=float, default=1.0)
    ap.add_argument("--n-estimators", type=int, default=100)
    args = ap.parse_args()

    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT)

    df = pd.read_csv("heart_data.csv")
    X, y = df.drop(columns=["num"]), df["num"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    with mlflow.start_run(run_name=f"{args.model}-run"):
        mlflow.log_param("model_kind", args.model)
        
        # Build pipeline for reproducibility
        if args.model == "logreg":
            mlflow.log_param("C", args.C)
            clf = LogisticRegression(C=args.C, max_iter=1000)
        else:
            mlflow.log_param("n_estimators", args.n_estimators)
            clf = RandomForestClassifier(n_estimators=args.n_estimators, random_state=42)
            
        pipe = Pipeline([
            ('scaler', StandardScaler()),
            ('classifier', clf)
        ])

        # Train
        pipe.fit(X_tr, y_tr)

        # Evaluate
        proba = pipe.predict_proba(X_te)[:, 1]
        preds = pipe.predict(X_te)
        
        metrics = {
            "accuracy": accuracy_score(y_te, preds),
            "precision": precision_score(y_te, preds),
            "recall": recall_score(y_te, preds),
            "roc_auc": roc_auc_score(y_te, proba),
            "f1_score": 2 * (precision_score(y_te, preds) * recall_score(y_te, preds)) / (precision_score(y_te, preds) + recall_score(y_te, preds))
        }
        mlflow.log_metrics(metrics)

        # Log Model
        mlflow.sklearn.log_model(pipe, artifact_path="model")
        print(f"Model logged. AUC: {metrics['roc_auc']:.4f}, F1 Score: {metrics['f1_score']:.4f}, accuracy: {metrics['accuracy']:.4f}, precision: {metrics['precision']:.4f}, recall: {metrics['recall']:.4f}")

if __name__ == "__main__":
    main()