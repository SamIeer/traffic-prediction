import streamlit as st
import folium
from folium.plugins import HeatMap, FastMarkerCluster
from streamlit_folium import st_folium
import pandas as pd
import matplotlib.colors as mcolors

# ---- CONFIG ----
st.set_page_config(layout="wide")
st.title("🚦 Delhi Traffic Prediction Dashboard")

# ---- LOAD & CACHE DATA ----
@st.cache_data
def load_cleaned():
    df = pd.read_csv("Dataset/gtfs_cleaned.csv")  # Replace with your path
    return df

cleaned = load_cleaned()

# ---- UI LAYOUT ----
left, right = st.columns([2, 3])

# ---- LEFT PANEL ----
with left:
    st.header("📍 Plan a Route")

    # Unique Stops
    stop_names = cleaned[['stop_id', 'stop_lat', 'stop_lon', 'stop_name']].drop_duplicates().reset_index(drop=True)

    stop_dict = {
        str(i): f"{row['stop_name']} (ID: {row['stop_id']})"
        for i, row in stop_names.iterrows()
    }

    source = st.selectbox("Select Source Stop", options=stop_dict.keys(), format_func=lambda x: stop_dict[x])
    dest = st.selectbox("Select Destination Stop", options=stop_dict.keys(), format_func=lambda x: stop_dict[x])
    hour = st.slider("Hour of Day", 0, 23, 8)

    if st.button("Predict Travel Time"):
        src = int(stop_names.iloc[int(source)]['stop_id'])
        dst = int(stop_names.iloc[int(dest)]['stop_id'])

        route_df = cleaned[(cleaned['stop_id'].isin([src, dst])) & (cleaned['hour_of_day'] == hour)]

        if not route_df.empty:
            try:
                src_time = route_df[route_df['stop_id'] == src]['arrival_sec'].values[0]
                dst_time = route_df[route_df['stop_id'] == dst]['arrival_sec'].values[0]
                predicted = abs(dst_time - src_time) // 60
                st.success(f"🕒 Estimated Travel Time: {predicted} minutes")
            except:
                st.warning("⚠️ Could not calculate — missing time data.")
        else:
            st.warning("⚠️ No matching route found at this hour.")

    # ---- Chart: Avg Travel Time by Hour ----
    st.subheader("📊 Avg Travel Time per Hour")
    hourly_avg = cleaned.groupby('hour_of_day')['travel_time_sec'].mean().reset_index()
    st.line_chart(hourly_avg.rename(columns={'travel_time_sec': 'Avg Travel Time (s)'}))

# ---- RIGHT PANEL ----
with right:
    st.header("🗺️ Interactive Route Map")

    delhi_map = folium.Map(location=[28.6139, 77.2090], zoom_start=12)

    # ---- Marker Clusters ----
    map_points = cleaned[['stop_lat', 'stop_lon']].dropna().drop_duplicates()
    map_sample = map_points.sample(n=min(1000, len(map_points)), random_state=42)
    marker_data = [(row['stop_lat'], row['stop_lon']) for _, row in map_sample.iterrows()]
    FastMarkerCluster(marker_data).add_to(delhi_map)

    # ---- Heatmap ----
    avg_tt = cleaned.groupby(['stop_lat', 'stop_lon'])['travel_time_sec'].mean().reset_index()
    heat_data = avg_tt.dropna()[['stop_lat', 'stop_lon', 'travel_time_sec']].values.tolist()
    HeatMap(heat_data, radius=15, blur=10).add_to(delhi_map)

    # ---- Route PolyLines ----
    st.subheader("🛤️ Display Route Lines")

    available_routes = cleaned[['trip_id']].dropna().drop_duplicates().sort_values('trip_id')
    selected_routes = st.multiselect("Select Routes", available_routes['trip_id'], default=available_routes['trip_id'].tolist()[:3])

    # Assign colors to routes
    route_colors = list(mcolors.TABLEAU_COLORS.values())
    route_color_map = {rid: route_colors[i % len(route_colors)] for i, rid in enumerate(available_routes['trip_id'])}

    for route in selected_routes:
        route_trips = cleaned[cleaned['trip_id'] == route]
        if route_trips.empty:
            continue

        stop_id = route_trips['stop_id'].dropna().unique()
        if len(stop_id) == 0:
            continue

        stop_id = stop_id[0]
        shape_data = route_trips[route_trips['stop_id'] == stop_id].sort_values('stop_sequence')
        shape_points = shape_data[['stop_lat', 'stop_lon']].dropna().values.tolist()

        folium.PolyLine(
            locations=shape_points,
            color=route_color_map[route],
            weight=4,
            popup=f"Route ID: {route}"
        ).add_to(delhi_map)

    # ---- Display Map ----
    st_data = st_folium(delhi_map, width=800, height=600)
