
import argparse
import json
import sys
from pathlib import Path


def check_model_quality(metrics_path: Path, max_mae: float, min_r2: float) -> bool:
    with metrics_path.open(encoding="utf-8") as file:
        metrics = json.load(file)

    mae = float(metrics["mae"])
    r2 = float(metrics["r2"])

    print(f"Model metrics: MAE={mae:.2f}, R2={r2:.4f}")
    print(f"Quality gate: MAE <= {max_mae}, R2 >= {min_r2}")

    if mae > max_mae or r2 < min_r2:
        print("QUALITY GATE FAILED")
        return False

    print("QUALITY GATE PASSED")
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", type=Path, default=Path("metrics.json"))
    parser.add_argument("--max-mae", type=float, default=2000)
    parser.add_argument("--min-r2", type=float, default=0.90)
    args = parser.parse_args()

    try:
        passed = check_model_quality(
            args.metrics,
            args.max_mae,
            args.min_r2,
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"Cannot validate model metrics: {exc}")
        sys.exit(1)

    if not passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
