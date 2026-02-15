import pandas as pd
import requests
import json
import time

print("Starting route precomputation...")

INPUT_PATH = "data/chennai_segmented.csv"
OUTPUT_PATH = "data/chennai_segmented_with_routes.csv"

df = pd.read_csv(INPUT_PATH)

def get_osrm_route(start, end):
    url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&geometries=geojson"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        coords = data["routes"][0]["geometry"]["coordinates"]
        return [(coord[1], coord[0]) for coord in coords]
    else:
        return [start, end]

routes = []

for (road, segment), group in df.groupby(["road_name", "segment_id"]):

    group = group.sort_values("latitude")
    coords = list(zip(group["latitude"], group["longitude"]))

    if len(coords) > 1:
        start = coords[0]
        end = coords[-1]
        route_coords = get_osrm_route(start, end)

        routes.append({
            "road_name": road,
            "segment_id": segment,
            "road_label": group["road_label"].iloc[0],
            "route_geometry": json.dumps(route_coords)
        })

        print(f"Processed: {road} - Segment {segment}")
        time.sleep(0.2)  # avoid hammering API

route_df = pd.DataFrame(routes)
route_df.to_csv(OUTPUT_PATH, index=False)

print("Route precomputation completed.")