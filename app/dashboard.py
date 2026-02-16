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
st.title("Chennai Smart Road Intelligence System")

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
# CITY LEVEL METRICS (NEW)
# ---------------------------
total_segments = len(df)
critical = len(df[df["road_label"] == 2])
moderate = len(df[df["road_label"] == 1])
good = len(df[df["road_label"] == 0])

avg_rhi_total = round(df["RHI"].mean(), 2)
critical_percent = round((critical / total_segments) * 100, 1)

st.markdown("## 📊 Road Health Overview")

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("City Health Index", avg_rhi_total)
k2.metric("Critical Segments", critical)
k3.metric("Moderate Segments", moderate)
k4.metric(" Healthy Segments", good)
k5.metric("% Critical Roads", f"{critical_percent}%")

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
st.markdown("## 🗺️ Live Road Condition Map")

m = folium.Map(
    location=[13.05, 80.23],
    zoom_start=11,
    tiles="CartoDB dark_matter"
)

color_map = {
    0: "#00FF88",
    1: "#FFA500",
    2: "#FF3B3B"
}

for (road, segment), group in filtered_df.groupby(["road_name", "segment_id"]):

    group = group.sort_index()
    coords = list(zip(group["latitude"], group["longitude"]))

    if len(coords) >= 2:

        label = group["road_label"].iloc[0]
        color = color_map.get(label, "#3388ff")

        avg_rhi = round(group["RHI"].mean(), 1)
        avg_rms = round(group["rms"].mean(), 2)

        popup_text = f"""
        <b>{road}</b><br>
        Segment: {segment}<br>
        RMS: {avg_rms}<br>
        RHI: {avg_rhi}<br>
        Priority: {group['priority'].iloc[0]}
        """

        folium.PolyLine(
            locations=coords,
            color=color,
            weight=14,
            opacity=0.25
        ).add_to(m)

        folium.PolyLine(
            locations=coords,
            color=color,
            weight=6,
            opacity=0.95,
            popup=popup_text
        ).add_to(m)

        folium.CircleMarker(
            location=coords[0],
            radius=4,
            color=color,
            fill=True,
            fill_opacity=1
        ).add_to(m)

        folium.CircleMarker(
            location=coords[-1],
            radius=4,
            color=color,
            fill=True,
            fill_opacity=1
        ).add_to(m)

# ---------------------------
# LEGEND
# ---------------------------
legend_html = """
<div style="
    position: fixed; 
    bottom: 40px; left: 40px; 
    width: 220px; 
    background-color: rgba(30,30,30,0.95);
    color: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 0 15px rgba(0,0,0,0.6);
    font-size: 14px;
    z-index: 9999;
">
<b>Road Condition</b><br><br>
<span style="color:#00FF88;">■</span> Good<br>
<span style="color:#FFA500;">■</span> Moderate<br>
<span style="color:#FF3B3B;">■</span> Critical
</div>
"""

m.get_root().html.add_child(folium.Element(legend_html))

st_folium(m, width=1400, height=600)

st.divider()

# ---------------------------
# ROAD RANKING TABLE (NEW)
# ---------------------------
st.markdown("##Road Ranking")

road_summary = (
    df.groupby("road_name")
    .agg(
        avg_rhi=("RHI", "mean"),
        critical_segments=("road_label", lambda x: (x == 2).sum())
    )
    .reset_index()
    .sort_values("avg_rhi")
)

st.dataframe(road_summary)

st.divider()

# ---------------------------
# RMS DISTRIBUTION
# ---------------------------
st.markdown("## RMS Distribution")
st.bar_chart(df["rms"])

st.divider()

# ---------------------------
# TOP CRITICAL ROADS
# ---------------------------
st.markdown("## Top High Priority Roads")

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

# Progress bar (NEW)
st.progress(int(avg_rhi))

# Maintenance recommendation (NEW)
if avg_rhi < 50:
    st.error("Immediate resurfacing required.")
elif avg_rhi < 75:
    st.warning("Schedule inspection within 30 days.")
else:
    st.success("Routine monitoring sufficient.")

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

# ---------------------------
# FOOTER
# ---------------------------
st.markdown("---")
st.markdown("PLS WORK 🙏🏻")
st.markdown("Developed by Goated G 🐐 Feb 14 | 2026")
st.markdown("Dm for more details or collaboration opportunities.")
st.markdown("All the data used for this project is simulated and does not represent real-world conditions & real world conditions are yet to be tested out.")
st.markdown("THANK YOU FOR VISITING!")
st.markdown("------")
