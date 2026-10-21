"""Train the car price regression model with MLflow tracking using params.yaml."""
import os
import subprocess
from pathlib import Path
import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
import yaml
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score

ROOT = Path(__file__).resolve().parents[1]

def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short=8", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "unknown"

def dvc_md5(dvc_file: Path) -> str:
    """md5 of the raw dataset as recorded by `dvc add` - the join key to dvc.lock."""
    try:
        return yaml.safe_load(dvc_file.read_text())["outs"][0]["md5"]
    except Exception:
        return "untracked"

def main() -> None:
    params = yaml.safe_load((ROOT / "params.yaml").read_text())["train"]

    # Nustato klasterio MLflow serverio adresą
    # Pirmiausia tikrina aplinkos kintamąjį, o jei jo nėra – naudoja vietinį port-forward adresą
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000"))

    # Nustatome eksperimento pavadinimą
    mlflow.set_experiment(os.environ.get("MLFLOW_EXPERIMENT_NAME", "car-price-prediction"))

    # Užkrauname paruoštus duomenis
    train = pd.read_csv(ROOT / "data/processed/train.csv")
    test = pd.read_csv(ROOT / "data/processed/test.csv")
    
    # Tikslinis kintamasis – kaina (price)
    x_train, y_train = train.drop("price", axis=1), train["price"]
    x_test, y_test = test.drop("price", axis=1), test["price"]

    run_name = f"ridge-alpha{params['alpha']}"
    with mlflow.start_run(run_name=run_name) as run:
        # Loginame parametrus į MLflow
        mlflow.log_params(params)

        # Pridedame MLOps atsekamumo žymes (Git commit, DVC md5) pagal NFR-09
        mlflow.set_tags({
            "git_commit": git_commit(),
            "dvc_raw_md5": dvc_md5(ROOT / "data/raw/cars.csv.dvc"),
            "model_family": "RidgeRegression",
        })
        
        # Registruojame duomenų šaltinį MLflow aplinkoje
        mlflow.log_input(
            mlflow.data.from_pandas(
                train, source="data/processed/train.csv", targets="price", name="train"
            ),
            context="training",
        )

        # Modelio inicijavimas ir mokymas
        model = Ridge(
            alpha=float(params["alpha"]),
            random_state=int(params["random_seed"]),
        )
        model.fit(x_train, y_train)
        preds = model.predict(x_test)
        
        # Skaičiuojame regresijos metrikas (MAE ir R2)
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)

        # Išsaugome modelį į MLflow
        info = mlflow.sklearn.log_model(
            model, name="model", input_example=x_train.head(3)
        )
        mlflow.log_metric("mae", mae, model_id=info.model_id)
        mlflow.log_metric("r2", r2, model_id=info.model_id)

        # Lokalus išsaugojimas sekančioms užduotims / DVC sekimui
        os.makedirs(ROOT / "models", exist_ok=True)
        joblib.dump(model, ROOT / "models/model.pkl")
        (ROOT / "models/run_id.txt").write_text(run.info.run_id + "\n")
        print(f"run_id={run.info.run_id} model_id={info.model_id} mae={mae:.2f} r2={r2:.4f}")

if __name__ == "__main__":
    main()