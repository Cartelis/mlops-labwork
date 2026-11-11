import pytest
from fastapi import HTTPException

from src import inference


def test_health_when_model_is_loaded(monkeypatch):
    monkeypatch.setattr(inference, "model", object())

    result = inference.health()

    assert result["status"] == "ok"
    assert result["model"] == "models:/car-price-model@champion"


def test_predict_returns_prediction(monkeypatch):
    class FakeModel:
        def predict(self, data):
            assert data.iloc[0]["year"] == 2020
            assert data.iloc[0]["mileage"] == 50000
            return [39933.77]

    monkeypatch.setattr(inference, "model", FakeModel())

    request = inference.PredictionRequest(
        year=2020,
        mileage=50000,
    )

    result = inference.predict(request)

    assert result.predicted_price == pytest.approx(39933.77)


def test_predict_when_model_is_not_loaded(monkeypatch):
    monkeypatch.setattr(inference, "model", None)

    request = inference.PredictionRequest(
        year=2020,
        mileage=50000,
    )

    with pytest.raises(HTTPException) as exc_info:
        inference.predict(request)

    assert exc_info.value.status_code == 503
