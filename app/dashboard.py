import requests
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

st.set_page_config(layout="wide")

# ---------------------------
# HEADER
# ---------------------------
st.title("🛣️ Chennai Smart Road Intelligence System")

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%d %b %Y | %H:%M:%S')}")
with col2:
    st.success("● SYSTEM ONLINE")

# ---------------------------
# LOAD DATA
# ---------------------------
DATA_PATH = "data/chennai_segmented.csv"
df = pd.read_csv(DATA_PATH)

# ---------------------------
# ROAD HEALTH INDEX (RHI)
# ---------------------------
def calculate_rhi(rms):
    return max(0, min(100, 100 - (rms * 40)))

df["RHI"] = df["rms"].apply(calculate_rhi)

def classify_priority(rhi):
    if rhi < 50:
        return "High"
    elif rhi < 75:
        return "Medium"
    else:
        return "Low"

df["priority"] = df["RHI"].apply(classify_priority)

# ---------------------------
# KPI METRICS
# ---------------------------
total_segments = len(df)
critical = len(df[df["road_label"] == 2])
moderate = len(df[df["road_label"] == 1])
good = len(df[df["road_label"] == 0])

avg_rhi_total = round(df["RHI"].mean(), 2)

st.markdown("## 📊 Road Health Overview")

k1, k2, k3, k4 = st.columns(4)

k1.metric("🚨 Critical Segments", critical)
k2.metric("⚠ Moderate Segments", moderate)
k3.metric("🟢 Healthy Segments", good)
k4.metric("📈 Avg Road Health Index", avg_rhi_total)

st.divider()

# ---------------------------
# SEVERITY FILTER
# ---------------------------
severity_filter = st.selectbox(
    "Filter Map by Condition",
    ["All", "Good", "Moderate", "Critical"]
)

filtered_df = df.copy()

if severity_filter == "Good":
    filtered_df = df[df["road_label"] == 0]
elif severity_filter == "Moderate":
    filtered_df = df[df["road_label"] == 1]
elif severity_filter == "Critical":
    filtered_df = df[df["road_label"] == 2]

# ---------------------------
# MAP SECTION
# ---------------------------
# ---------------------------
# MAP SECTION (OSRM ROAD SNAPPING)
# ---------------------------
st.markdown("## 🗺️ Live Road Condition Map")

m = folium.Map(location=[13.05, 80.23], zoom_start=12)

color_map = {
    0: "green",
    1: "orange",
    2: "red"
}

def get_osrm_route(start, end):
    url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}?overview=full&geometries=geojson"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        coords = data["routes"][0]["geometry"]["coordinates"]
        # OSRM gives [lon, lat], convert to [lat, lon]
        return [(coord[1], coord[0]) for coord in coords]
    else:
        return [start, end]

for (road, segment), group in df.groupby(["road_name", "segment_id"]):

    group = group.sort_values("latitude")

    coords = list(zip(group["latitude"], group["longitude"]))

    if len(coords) > 1:
        label = group["road_label"].iloc[0]
        color = color_map.get(label, "gray")

        start = coords[0]
        end = coords[-1]

        route_coords = get_osrm_route(start, end)

        folium.PolyLine(
            locations=route_coords,
            color=color,
            weight=6,
            opacity=0.9,
            tooltip=f"{road} | Segment {segment}"
        ).add_to(m)

st_folium(m, width=1400, height=600)

# ---------------------------
# LEGEND
# ---------------------------
st.markdown("### 🧭 Legend")
st.markdown("""
🟢 Good Road  
🟡 Moderate Condition  
🔴 Poor Road (High Priority)
""")

st.divider()

# ---------------------------
# RMS DISTRIBUTION
# ---------------------------
st.markdown("## 📊 RMS Distribution")
st.bar_chart(df["rms"])

st.divider()

# ---------------------------
# TOP CRITICAL ROADS
# ---------------------------
st.markdown("## 🚨 Top High Priority Roads")

critical_df = df[df["road_label"] == 2]

if not critical_df.empty:
    top_roads = (
        critical_df.groupby("road_name")
        .size()
        .sort_values(ascending=False)
        .head(5)
    )

    for road, count in top_roads.items():
        st.write(f"🔴 {road} — {count} Critical Segments")
else:
    st.success("No critical roads detected.")

st.divider()

# ---------------------------
# ROAD ANALYSIS
# ---------------------------
st.markdown("## 🔍 Road Analysis")

road_list = df["road_name"].unique()
selected_road = st.selectbox("Select Road", road_list)

road_data = df[df["road_name"] == selected_road]

st.line_chart(road_data["rms"])

avg_rhi = round(road_data["RHI"].mean(), 2)

st.metric("Average Road Health Index", avg_rhi)

if avg_rhi < 50:
    st.error("Overall Condition: Critical")
elif avg_rhi < 75:
    st.warning("Overall Condition: Moderate")
else:
    st.success("Overall Condition: Healthy")

st.markdown(f"**Total Segments:** {len(road_data)}")

st.divider()

# ---------------------------
# DOWNLOAD OPTION
# ---------------------------
st.markdown("## ⬇ Export Data")

st.download_button(
    label="Download Road Report CSV",
    data=df.to_csv(index=False),
    file_name="chennai_road_report.csv",
    mime="text/csv"
)