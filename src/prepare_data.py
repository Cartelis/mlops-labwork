"""Prepare train/test split. Run: python src/prepare_data.py"""
import os
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/cars.csv"
OUT_DIR = ROOT / "data/processed"
TEST_SIZE = 0.2
SEED = 42

def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    df = pd.read_csv(RAW)
    
    # Regresijoje nenaudojame stratify, nes 'price' yra tolydus kintamasis
    train, test = train_test_split(
        df, test_size=TEST_SIZE, random_state=SEED
    )
    
    train.to_csv(OUT_DIR / "train.csv", index=False)
    test.to_csv(OUT_DIR / "test.csv", index=False)
    print(f"Train: {len(train)}, Test: {len(test)}")

if __name__ == "__main__":
    main()