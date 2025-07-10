import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import pandas as pd

cleaned = pd.read_csv("Dataset\gtfs_cleaned.csv")

# ---- UI Setup ----
st.set_page_config(layout="wide")
st.title(" Traffic Prediction Dashboard")

left, right = st.columns([2, 3])

# ---- Left Panel: Inputs and Charts ----
with left:
    st.header("Plan a Route")

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
                st.success(f"🚇 Estimated Travel Time: {predicted} minutes")
            except:
                st.warning("❌ Could not calculate — data might be missing.")
        else:
            st.warning("⚠️ No matching route found at this hour.")

    # Chart
    st.subheader("📊 Avg Travel Time per Hour")
    avg_hourly = cleaned.groupby('hour_of_day')['travel_time_sec'].mean().reset_index()
    st.line_chart(avg_hourly.rename(columns={'travel_time_sec': 'Avg Travel Time (s)'}))

# ---- Right Panel: Folium Map with Stops + Heatmap ----
with right:
    st.header("Interactive  Route Map")

    delhi_map = folium.Map(location=[28.6139, 77.2090], zoom_start=12)

    # Add stop points
    for _, row in cleaned.iterrows():
        if pd.notnull(row['stop_lat']) and pd.notnull(row['stop_lon']):
            folium.CircleMarker(
                location=[row['stop_lat'], row['stop_lon']],
                radius=3,
                color='blue',
                fill=True,
                fill_opacity=0.7,
                popup=f"Stop ID: {row['stop_id']}, Trip: {row['trip_id']}"
            ).add_to(delhi_map)

    # Add heatmap (ensure no NaNs)
    avg_tt = cleaned.groupby(['stop_lat', 'stop_lon'])['travel_time_sec'].mean().reset_index()
    heat_data = [
        [row['stop_lat'], row['stop_lon'], row['travel_time_sec']] 
        for _, row in avg_tt.iterrows() 
        if pd.notnull(row['stop_lat']) and pd.notnull(row['stop_lon'])
    ]
    HeatMap(heat_data, radius=15, blur=10).add_to(delhi_map)

    # Render map
    st_folium(delhi_map, width=800, height=600)
