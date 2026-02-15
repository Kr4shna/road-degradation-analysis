import pandas as pd
import numpy as np
import os

SEGMENT_LENGTH_METERS = 500
POINTS_PER_SEGMENT = 10
TOTAL_SEGMENTS = 8

road_profiles = {
    "OMR": "poor",
    "ECR": "moderate",
    "Mount Road": "good",
    "Velachery": "mixed",
    "Anna Nagar": "good"
}

road_starts = {
    "OMR": (12.9150, 80.2300),
    "ECR": (12.9000, 80.2500),
    "Mount Road": (13.0600, 80.2700),
    "Velachery": (12.9750, 80.2200),
    "Anna Nagar": (13.0850, 80.2100)
}

def generate_rms(profile):
    if profile == "good":
        return np.random.uniform(0.55, 0.65)
    elif profile == "moderate":
        return np.random.uniform(0.75, 1.0)
    elif profile == "poor":
        return np.random.uniform(1.3, 2.2)
    elif profile == "mixed":
        return np.random.choice([
            np.random.uniform(0.55, 0.65),
            np.random.uniform(0.75, 1.0),
            np.random.uniform(1.3, 2.2)
        ])

def simulate():
    rows = []

    for road_name, profile in road_profiles.items():
        lat, lon = road_starts[road_name]

        for segment in range(TOTAL_SEGMENTS):
            for point in range(POINTS_PER_SEGMENT):
                rms = generate_rms(profile)

                rows.append({
                    "road_name": road_name,
                    "latitude": lat,
                    "longitude": lon,
                    "rms": rms
                })

                lat += 0.0003
                lon += 0.0003

    df = pd.DataFrame(rows)

    os.makedirs("data/raw_data", exist_ok=True)
    df.to_csv("data/raw_data/simulated_chennai_trips.csv", index=False)

    print("Simulation complete.")
    print("Rows generated:", len(df))

if __name__ == "__main__":
    simulate()