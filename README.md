# Delhi Traffic Prediction using GTFS & OpenStreetMap

A machine learning-powered system to predict travel time between metro stations in Delhi using GTFS transit data. It visualizes live congestion, stop-to-stop delay, and optimal routes using interactive maps and charts.

---

##  Project Description

This project uses **General Transit Feed Specification (GTFS)** datasets (stops, stop_times, trips, routes, shapes) to build a **Random Forest-based model** for travel time prediction across metro stops in Delhi. The final outcome is an interactive **Streamlit dashboard** using **Folium** maps, travel estimations, and route visuals.

---

##  Data Preprocessing & Feature Engineering

All GTFS `.txt` files were processed using pandas in a Jupyter notebook:

###  Steps Involved:
1. **Merged `stop_times.txt` with `stops.txt`** to get latitude/longitude and timestamps.
2. **Sorted by `trip_id` and `stop_sequence`** to ensure sequential travel.
3. **Calculated `travel_time_sec`** between consecutive stops.
4. **Extracted time features**: hour of day, service type (`weekday`, `saturday`, etc.).
5. **Merged with `trips.txt`** to get `route_id`, `direction_id`, and shape ID.
6. **Handled anomalies** like missing values and duplicated trips.
7. **Saved the final DataFrame** as `gtfs_cleaned.parquet`.

### 🧾 Main Cleaned File: `gtfs_cleaned.parquet`
| Feature               | Description                         |
|------------------------|-------------------------------------|
| trip_id               | Unique trip reference               |
| stop_sequence         | Order of stop in trip               |
| arrival_time / dep.   | Timestamps from stop_times.txt      |
| stop_lat / stop_lon   | From stops.txt                      |
| travel_time_sec       | Time between current and next stop  |
| route_id              | Metro line ID                       |
| direction_id          | Direction (0 or 1)                  |
| service_id            | weekday/weekend/saturday            |
| hour                  | Extracted from time for patterning  |
| shape_dist_traveled   | Distance covered on shape route     |

###  Libraries Used (Preprocessing):
- `pandas`, `numpy`
- `datetime`, `pyarrow`
- `sklearn.model_selection`, `sklearn.ensemble.RandomForestRegressor`
- `matplotlib.pyplot` (for visual EDA)

---

##  Streamlit Dashboard

An interactive UI for users to:

- Select source and destination metro stations
- Choose hour of the day
- Predict travel time using trained ML model
- View metro stops and congestion heatmap on **Folium (OpenStreetMap)**
- Visualize route paths based on `shapes.txt`
- Display signal points and their status

### 🗺 Dashboard Features:

| Feature | Description |
|--------|-------------|
| **Folium Map** | OpenStreetMap centered on Delhi |
| **Circle Markers** | Show congestion on stops |
| **Heatmap** | Density based on historical traffic |
| **Stop Info** | Hover to view arrival/departure time |
| **Prediction Box** | Select source → destination → hour |
| **Graph** | Line graph of predicted vs actual |
| **Route Visualizer** | Draws routes using `shapes.txt` |

### Libraries Used (Dashboard):
- `streamlit`
- `folium`
- `streamlit_folium`
- `pandas`, `joblib` (for loading model)
- `geopy` (optional: for user coordinates)

---

##  Docker Support

You can containerize and deploy the app using Docker:

###  Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "dashboard/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
