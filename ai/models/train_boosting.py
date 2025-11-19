"""Entrena un modelo de boosting simple sobre un dataset de perfiles y guarda con pickle.

Salida: `ai/models/boosting_model.pkl`

Por defecto usa `ai/models/user_dataset.csv`. Puedes pasar otro CSV como argumento
al llamar a `train(csv_path=...)`.
"""
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

BASE_DIR = Path(__file__).resolve().parent
USER_DATA_CSV = BASE_DIR / "user_dataset.csv"
MODEL_OUT = BASE_DIR / "boosting_model.pkl"


def train(csv_path: Path = USER_DATA_CSV, out_path: Path = MODEL_OUT):
	if not csv_path.exists():
		raise FileNotFoundError(
			f"Dataset no encontrado: {csv_path}."
		)

	df = pd.read_csv(csv_path)

	features = [
		"age",
		"income",
		"household_size",
		"vegetarian",
		"shopping_freq_per_month",
		"avg_basket_value",
	]
	X = df[features].values
	y = df["price_sensitivity"].values

	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

	pipeline = Pipeline([
		("scaler", StandardScaler()),
		("gb", GradientBoostingRegressor(random_state=42, n_estimators=100, learning_rate=0.1)),
	])

	pipeline.fit(X_train, y_train)

	preds = pipeline.predict(X_test)
	mae = mean_absolute_error(y_test, preds)
	r2 = r2_score(y_test, preds)

	print(f"GradientBoostingRegressor: MAE={mae:.4f}, R2={r2:.4f}")

	# Guarda el pipeline (escalado + modelo)
	out_path.parent.mkdir(parents=True, exist_ok=True)
	with open(out_path, "wb") as f:
		pickle.dump(pipeline, f)

	print(f"Model saved to {out_path}")


if __name__ == "__main__":
	train()
