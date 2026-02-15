import pandas as pd
import os

print("Starting segmentation...")

INPUT_PATH = "data/chennai_roads_with_predictions.csv"
OUTPUT_PATH = "data/chennai_segmented.csv"

if not os.path.exists(INPUT_PATH):
    raise FileNotFoundError(f"Input file not found at {INPUT_PATH}")

# Load predicted dataset
df = pd.read_csv(INPUT_PATH)
print(f"Dataset loaded. Total rows: {len(df)}")

SEGMENT_SIZE = 5  # number of consecutive points per segment

# Sort properly (very important)
df = df.sort_values(["road_name", "latitude", "longitude"])

# Assign segment IDs WITHOUT averaging
df["segment_id"] = df.groupby("road_name").cumcount() // SEGMENT_SIZE

# Save directly (keep all lat/long rows)
df.to_csv(OUTPUT_PATH, index=False)

print("Segmentation completed successfully.")
print(f"Saved segmented file to: {OUTPUT_PATH}")