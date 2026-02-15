import pandas as pd
import joblib
import os

print("Starting road prediction pipeline...\n")

# -------------------------------------------------
# PATH CONFIGURATION (RUNNING FROM PROJECT ROOT)
# -------------------------------------------------
MODEL_PATH = "app/road_condition_model_final.pkl"
INPUT_PATH = "data/chennai_roads.csv"
OUTPUT_PATH = "data/chennai_roads_with_predictions.csv"

# -------------------------------------------------
# CHECK FILE EXISTENCE
# -------------------------------------------------
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at {MODEL_PATH}")

if not os.path.exists(INPUT_PATH):
    raise FileNotFoundError(f"Dataset not found at {INPUT_PATH}")

# -------------------------------------------------
# LOAD MODEL
# -------------------------------------------------
model = joblib.load(MODEL_PATH)
print("Model loaded successfully.")

# -------------------------------------------------
# LOAD DATASET
# -------------------------------------------------
df = pd.read_csv(INPUT_PATH)
print(f"Dataset loaded. Total rows: {len(df)}")

# -------------------------------------------------
# VALIDATE REQUIRED COLUMN
# -------------------------------------------------
if "rms" not in df.columns:
    raise ValueError("Column 'rms' not found in dataset.")

# -------------------------------------------------
# PREPARE FEATURES
# Model trained on: mean_rms + std_rms
# We simulate std_rms for map visualization
# -------------------------------------------------
# Rename rms to mean_rms to match training feature
df["mean_rms"] = df["rms"]
df["std_rms"] = 0.05

X = df[["mean_rms", "std_rms"]]

# -------------------------------------------------
# PREDICTION
# -------------------------------------------------
df["road_label"] = model.predict(X)

print("Prediction completed.")

# -------------------------------------------------
# SAVE OUTPUT
# -------------------------------------------------
df.to_csv(OUTPUT_PATH, index=False)

print(f"Saved predicted dataset to: {OUTPUT_PATH}")
print("\nRoad prediction pipeline finished successfully.")