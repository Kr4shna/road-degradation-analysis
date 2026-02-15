import pandas as pd
import numpy as np
import time
import joblib
from collections import deque
from datetime import datetime
import os

# -------------------------------------------------
# LOAD TRAINED MACHINE LEARNING MODEL
# -------------------------------------------------
model = joblib.load("road_condition_model_final.pkl")

# -------------------------------------------------
# LOAD SENSOR DATA (SIMULATED REAL-TIME INPUT)
# -------------------------------------------------
df = pd.read_csv("/Users/krishnacharan/Desktop/Random/road_ml/raw_data/transition_test.csv")
skip_blank_lines=True

# -------------------------------------------------
# CONFIGURATION
# -------------------------------------------------
WINDOW_SIZE = 5              # small for stress testing
SAMPLE_DELAY = 0.05          # seconds (~20 Hz)
GRAVITY = 9.81               # normalization factor
SHOCK_RMS_THRESHOLD = 0.15    # tuned for extreme potholes

label_map = {
    0: "GOOD ROAD",
    1: "MODERATE ROAD",
    2: "POOR ROAD"
}

# -------------------------------------------------
# TEMPORAL BUFFERS
# -------------------------------------------------
buffer = []
trend_buffer = deque(maxlen=5)

# -------------------------------------------------
# LOGGING SETUP
# -------------------------------------------------
os.makedirs("logs", exist_ok=True)
log_file = "logs/realtime_predictions.csv"

if not os.path.exists(log_file):
    with open(log_file, "w") as f:
        f.write(
            "timestamp,mean_rms,std_rms,predicted_label,"
            "confidence,RHI,priority\n"
        )

print("\nReal-Time Road Condition Monitoring Started\n")

# -------------------------------------------------
# REAL-TIME SIMULATION LOOP
# -------------------------------------------------
for _, row in df.iterrows():
    ax = row["accelerometerX"]
    ay = row["accelerometerY"]
    az = row["accelerometerZ"]

    # -----------------------------
    # RMS COMPUTATION + NORMALIZATION
    # -----------------------------
    rms = np.sqrt((ax**2 + ay**2 + az**2) / 3)
    normalized_rms = rms / GRAVITY
    buffer.append(normalized_rms)

    # -----------------------------
    # WHEN WINDOW IS FULL → INFERENCE
    # -----------------------------
    if len(buffer) == WINDOW_SIZE:
        mean_rms = np.mean(buffer)
        std_rms = np.std(buffer)

        # -------------------------
        # ML PREDICTION + CONFIDENCE
        # -------------------------
        probabilities = model.predict_proba([[mean_rms, std_rms]])[0]
        prediction = int(np.argmax(probabilities))
        confidence = max(probabilities) * 100

        # -------------------------
        # SHOCK FREQUENCY LOGIC (INDIAN ROAD ADAPTATION)
        # -------------------------
        shock_count = sum(1 for v in buffer if v > SHOCK_RMS_THRESHOLD)
        shock_ratio = shock_count / len(buffer)

        # Interpret shock frequency instead of single spikes
        if shock_ratio > 0.4:
            prediction = 2   # POOR ROAD (frequent shocks)
            confidence = max(confidence, 90.0)
        elif shock_ratio > 0.15:
            prediction = 1   # MODERATE ROAD (occasional shocks)
            confidence = max(confidence, 70.0)
        # else: keep ML prediction

        trend_buffer.append(prediction)

        # -------------------------
        # ROAD HEALTH INDEX (RHI)
        # -------------------------
        RHI = max(0, min(100, 100 - (mean_rms * 100)))

        # -------------------------
        # TEMPORAL PERSISTENCE CHECK
        # -------------------------
        persistent_poor = trend_buffer.count(2) >= 3

        # -------------------------
        # MAINTENANCE PRIORITY LOGIC
        # -------------------------
        if RHI < 40 or persistent_poor:
            priority = "HIGH PRIORITY"
        elif RHI < 70:
            priority = "MEDIUM PRIORITY"
        else:
            priority = "LOW PRIORITY"

        # -------------------------
        # CONSOLE OUTPUT
        # -------------------------
        print("======================================")
        print(f"Road Condition     : {label_map[prediction]}")
        print(f"Confidence Score   : {confidence:.2f}%")
        print(f"Road Health Index  : {RHI:.2f} / 100")
        print(f"Recent Trend       : {[label_map[p] for p in trend_buffer]}")
        print(f"Maintenance Action: {priority}")
        print("======================================\n")

        # -------------------------
        # LOG TO CSV
        # -------------------------
        with open(log_file, "a") as f:
            f.write(
                f"{datetime.now()},{mean_rms:.4f},{std_rms:.4f},"
                f"{prediction},{confidence:.2f},{RHI:.2f},{priority}\n"
            )

        buffer.clear()

    time.sleep(SAMPLE_DELAY)
print("Window number:", len(trend_buffer))
print("Total rows loaded:", len(df))

print("Simulation completed.")