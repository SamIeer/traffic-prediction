# 🚦 Traffic Prediction for Delhi

A machine learning pipeline and interactive dashboard that predicts traffic congestion and travel time in Delhi using GTFS and open-source road network data.

---

## 📦 What’s Inside

### 🔍 Data Processing
Processes GTFS data files:
- `stop_times.txt`, `stops.txt`, `trips.txt`, `routes.txt`, `shapes.txt`

Transforms them to:
- Merge stop coordinates with timings
- Calculate inter-stop travel durations
- Extract time-based features (hour, weekday/weekend)
- Clean anomalies and prepare a modeling-ready dataset (`gtfs_cleaned.parquet`)

### 🤖 Machine Learning (Planned/Optional)
- Predict travel time between stops using:
  - Random Forest 
  - Time Series models (LSTM, GRU)
  - Graph Neural Networks (future enhancement)

### 🖥️ Streamlit Dashboard
An interactive dashboard built using **Streamlit** + **Folium**:
- **Route Planner**: Select source, destination, and time → predict travel time
- **Traffic Trends**: Visual charts of average congestion
- **Delhi Map**: Real-time heatmap of congestion levels and traffic signals
- **Folium Interactivity**: Popup markers show congestion & average speed

---

## 🐳 Docker Support

Deploy easily using Docker:

```bash
# Build the container
docker build -t delhi-traffic-app .

# Run the app
docker run -p 8501:8501 delhi-traffic-app
