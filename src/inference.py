import os
from contextlib import asynccontextmanager

import mlflow
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

MODEL_URI = "models:/car-price-model@champion"
MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://mlflow-server.mlops-labwork.svc:5000",
)

model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    model = mlflow.pyfunc.load_model(MODEL_URI)

    yield

    model = None

app = FastAPI(
    title="Car Price Prediction API",
    version="1.0.0",
    lifespan=lifespan,
)

class PredictionRequest(BaseModel):
    year: int = Field(..., description="Car manufacturing year")
    mileage: int = Field(..., ge=0, description="Car mileage")

class PredictionResponse(BaseModel):
    predicted_price: float

@app.get("/health")
def health():
    return {
        "status": "ok" if model is not None else "unavailable",
        "model": MODEL_URI,
    }

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded",
        )

    try:
        input_data = pd.DataFrame(
            [{
                "year": request.year,
                "mileage": request.mileage,
            }]
        )

        prediction = model.predict(input_data)

        return PredictionResponse(
            predicted_price=float(prediction[0])
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc
