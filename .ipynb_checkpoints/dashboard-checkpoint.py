import streamlit as st
import folium
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_folium import st_folium

# Mock LLM function (replace with xAI API call)
def mock_llm_prediction(start, dest, time):
    return f"Travel time from {start} to {dest} at {time}: 45 minutes, moderate congestion on NH48"

# Sample data (replace with Kaggle/OpenStreetMap data)
data = pd.DataFrame({
    'lat': [28.6139, 28.6250, 28.6000],
    'lon': [77.2090, 77.2200, 77.2000],
    'congestion_score': [0.8, 0.4, 0.9],
    'avg_speed': [12, 25, 10],
    'time': ['2025-06-02 08:00', '2025-06-02 08:00', '2025-06-02 08:00']
})

# Dashboard layout
st.title("Smart Cities Traffic Prediction Dashboard")

# Two-column layout
col1, col2 = st.columns([3, 2])

# Left column: Map
with col1:
    st.subheader("Traffic Map")
    m = folium.Map(location=[28.6139, 77.2090], zoom_start=12)  # Delhi
    for idx, row in data.iterrows():
        color = 'red' if row['congestion_score'] > 0.7 else 'green'
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=row['congestion_score'] * 10,
            color=color,
            fill=True,
            popup=f"Speed: {row['avg_speed']} km/h\nCongestion: {row['congestion_score']}"
        ).add_to(m)
    st_folium(m, width=500, height=400)

# Right column: Input form and visualizations
with col2:
    st.subheader("Predict Traffic")
    start = st.text_input("Starting Point", "Connaught Place")
    dest = st.text_input("Destination", "Delhi Airport")
    time = st.text_input("Travel Time", "8 AM")
    if st.button("Predict"):
        prediction = mock_llm_prediction(start, dest, time)
        st.write(prediction)

    st.subheader("Traffic Trends")
    # Sample line chart
    fig, ax = plt.subplots()
    ax.plot(data['time'], data['congestion_score'], marker='o', color='blue')
    ax.set_xlabel("Time")
    ax.set_ylabel("Congestion Score")
    st.pyplot(fig)

# Sample bar chart
st.subheader("Congestion by Road")
fig, ax = plt.subplots()
ax.bar(['NH48', 'MG Road', 'Ring Road'], data['congestion_score'], color=['red', 'green', 'red'])
ax.set_ylabel("Congestion Score")
st.pyplot(fig)