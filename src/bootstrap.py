"""Generate sample car data and train a baseline regression model for local/Docker testing."""
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split

SEED = 42
N_SAMPLES = 1000

def main() -> None:
    rng = np.random.default_rng(SEED)
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("models", exist_ok=True)

    # Sugeneruojame sintetinį automobilių rinkinį
    year = rng.integers(2010, 2024, size=N_SAMPLES)
    mileage = rng.integers(10000, 250000, size=N_SAMPLES)
    
    # Kaina logiškai priklauso nuo metų (naujesnis = brangesnis) ir ridos (didesnė rida = pigesnis)
    price = 30000 + (year - 2010) * 1500 - (mileage / 10) + rng.normal(0, 2000, size=N_SAMPLES)
    price = np.clip(price, 1000, 80000) # kad nebūtų neigiamų kainų

    df = pd.DataFrame({
        "year": year,
        "mileage": mileage,
        "price": price
    })
    
    # 1. Išsaugome raw duomenis
    df.to_csv("data/raw/cars.csv", index=False)
    print(f"Wrote data/raw/cars.csv ({len(df)} rows)")

    # 2. Skaidome į train/test (regresijoje nenaudojame stratify!)
    train, test = train_test_split(df, test_size=0.2, random_state=SEED)
    train.to_csv("data/processed/train.csv", index=False)
    test.to_csv("data/processed/test.csv", index=False)

    # 3. Apmokome bazinį Ridge modelį
    model = Ridge(alpha=1.0, random_state=SEED)
    model.fit(train.drop("price", axis=1), train["price"])
    
    # Išsaugome pradinį modelį
    joblib.dump(model, "models/model.pkl")
    print("Wrote models/model.pkl")

if __name__ == "__main__":
    main()