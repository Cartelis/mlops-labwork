import json

from scripts.check_model_gate import check_model_quality


def test_quality_gate_passes(tmp_path):
    metrics = tmp_path / "metrics.json"
    metrics.write_text(
        json.dumps({"mae": 1788.53, "r2": 0.9433}),
        encoding="utf-8",
    )

    assert check_model_quality(metrics, 2000, 0.90) is True


def test_quality_gate_fails_on_high_mae(tmp_path):
    metrics = tmp_path / "metrics.json"
    metrics.write_text(
        json.dumps({"mae": 2500, "r2": 0.95}),
        encoding="utf-8",
    )

    assert check_model_quality(metrics, 2000, 0.90) is False


def test_quality_gate_fails_on_low_r2(tmp_path):
    metrics = tmp_path / "metrics.json"
    metrics.write_text(
        json.dumps({"mae": 1500, "r2": 0.80}),
        encoding="utf-8",
    )

    assert check_model_quality(metrics, 2000, 0.90) is False
