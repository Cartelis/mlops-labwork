import pytest

from src.hpo import check_model_quality


def test_quality_gate_passes():
    check_model_quality(mae=1788.38, r2=0.9433)


def test_quality_gate_fails_on_high_mae():
    with pytest.raises(RuntimeError, match="Model quality gate failed"):
        check_model_quality(mae=2500, r2=0.95)


def test_quality_gate_fails_on_low_r2():
    with pytest.raises(RuntimeError, match="Model quality gate failed"):
        check_model_quality(mae=1500, r2=0.80)