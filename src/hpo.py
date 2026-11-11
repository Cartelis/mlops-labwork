
import os
import yaml
import joblib
import optuna
import mlflow
import mlflow.sklearn
import pandas as pd
import subprocess

from pathlib import Path
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from mlflow.tracking import MlflowClient

ROOT = Path(__file__).resolve().parents[1]
TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://localhost:5000",
)
EXPERIMENT_NAME = os.getenv(
    "MLFLOW_EXPERIMENT_NAME",
    "car-price-prediction",
)
REGISTERED_MODEL_NAME = "car-price-model"
N_TRIALS = int(os.getenv("N_TRIALS", "5"))
SEED = int(os.getenv("RANDOM_SEED", "42"))


mlflow.set_tracking_uri(TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

def get_dvc_raw_md5():
    dvc_file = ROOT / "data/raw/cars.csv.dvc"
    metadata = yaml.safe_load(dvc_file.read_text(encoding="utf-8"))
    return metadata["outs"][0]["md5"]

def git_commit() -> str:
    env_commit = os.getenv("GIT_COMMIT")
    if env_commit:
        return env_commit

    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short=8", "HEAD"],
            cwd=ROOT,
            text=True,
        ).strip()
    except Exception:
        return "unknown"

def main():
    train = pd.read_csv(ROOT / "data/processed/train.csv")
    test = pd.read_csv(ROOT / "data/processed/test.csv")

    X_train = train.drop(columns=["price"])
    y_train = train["price"]
    X_test = test.drop(columns=["price"])
    y_test = test["price"]

    study = optuna.create_study(
        direction="minimize",
        sampler=optuna.samplers.TPESampler(seed=SEED),
    )

    mlflow.enable_system_metrics_logging()

    with mlflow.start_run(run_name="ridge-hpo") as parent_run:
        mlflow.set_tag("git_commit", git_commit())
        mlflow.set_tag("dvc_raw_md5", get_dvc_raw_md5())
        mlflow.set_tag("random_seed", str(SEED))
        mlflow.set_tag("model_family", "Ridge")
        mlflow.log_artifact(
            str(ROOT / "requirements-u2.txt"),
            artifact_path="environment",
        )
        mlflow.log_param("n_trials", N_TRIALS)

        dataset = mlflow.data.from_pandas(
            train,
            source="data/processed/train.csv",
            name="car-training-data",
            targets="price",
        )
        mlflow.log_input(dataset, context="training")

        def objective(trial):
            alpha = trial.suggest_float("alpha", 0.01, 100.0, log=True)

            with mlflow.start_run(
                nested=True,
                run_name=f"trial-{trial.number}",
            ):
                model = Ridge(alpha=alpha)
                model.fit(X_train, y_train)

                predictions = model.predict(X_test)
                mae = mean_absolute_error(y_test, predictions)
                r2 = r2_score(y_test, predictions)

                mlflow.log_param("alpha", alpha)
                mlflow.log_metric("mae", mae, step=trial.number)
                mlflow.log_metric("r2", r2, step=trial.number)
                mlflow.set_tag("trial_number", str(trial.number))

            return mae

        study.optimize(objective, n_trials=N_TRIALS)

        best_alpha = study.best_params["alpha"]
        best_model = Ridge(alpha=best_alpha)
        best_model.fit(X_train, y_train)

        predictions = best_model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)

        mlflow.log_metric("best_mae", mae)
        mlflow.log_metric("best_r2", r2)
        mlflow.log_param("best_alpha", best_alpha)

        mlflow.sklearn.log_model(
            best_model,
            name="model",
            input_example=X_train.head(3),
            pip_requirements=str(ROOT / "requirements-u2.txt"),
        )

        # Register the trained model and assign the champion alias.
        model_uri = f"runs:/{parent_run.info.run_id}/model"
        registered = mlflow.register_model(
            model_uri=model_uri,
            name=REGISTERED_MODEL_NAME,
        )

        client = MlflowClient()
        client.set_registered_model_alias(
            REGISTERED_MODEL_NAME,
            "champion",
            registered.version,
        )

        print(f"Parent run: {parent_run.info.run_id}")
        print(f"Best alpha: {best_alpha}")
        print(f"MAE: {mae:.2f}")
        print(f"R2: {r2:.4f}")
        print(f"Registered model version: {registered.version}")
        print(f"Alias: models:/{REGISTERED_MODEL_NAME}@champion")

if __name__ == "__main__":
    main()
