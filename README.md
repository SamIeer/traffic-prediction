# 🚦 Delhi Traffic Prediction & Route Analysis (OpenStreetMap)

A **research-oriented traffic analysis and route visualization system for Delhi** using **OpenStreetMap, TomTom APIs, and Streamlit**.

This project focuses on **route planning, traffic delay analysis, and explainable experimentation with machine learning**, rather than claiming production-grade traffic prediction.

---

## 📌 Project Overview

This project provides an interactive dashboard that allows users to:

- Select a **source and destination** in Delhi
- Visualize routes on **OpenStreetMap (Folium)**
- Fetch real routing data (distance, ETA, traffic delay) from **TomTom**
- Generate a **natural-language travel advisory** using an LLM
- Experiment with **ML-based traffic classification** (research / experimental)

---

## ⚠️ Important Note

The current machine-learning model is **experimental** and **not used as the single source of truth** for traffic visualization.

- Routing, ETA, and delay values come from **TomTom APIs**
- ML outputs are used **only for research and analysis**, not for live traffic decisions

---

## 🧠 System Architecture

User Input (Source, Destination, Mode)
↓
TomTom Geocoding API
↓
TomTom Routing API (real road data)
↓
• Distance
• ETA
• Traffic Delay
↓
OpenWeather API → Weather context
↓
LLM (Groq) → Travel advisory (text)
↓
Folium + Streamlit → Interactive Map UI


The ML component runs **in parallel** for experimentation and analysis.

---

## 📊 Data Preprocessing & Feature Engineering

GTFS (General Transit Feed Specification) data is used **only for ML experimentation**, not for live road traffic.

### Steps Performed

- Merged `stop_times.txt` with `stops.txt`
- Sorted by `trip_id` and `stop_sequence`
- Computed `travel_time_sec` between stops
- Extracted temporal features:
  - Hour of day
  - Service type (weekday / weekend)
- Joined `trips.txt` for route and direction metadata
- Cleaned anomalies and missing values
- Saved cleaned data as `gtfs_cleaned.csv`
- Created heuristic labels → `gtfs_labeled.csv`

---

## 📁 Key Files

| File | Purpose |
|----|--------|
| `gtfs_cleaned.csv` | Cleaned GTFS dataset |
| `gtfs_labeled.csv` | Heuristically labeled traffic data |
| `traffic_rf_model.pkl` | Experimental ML model |
| `label_encoder.pkl` | Label encoder |

---

## ⚠️ Known Limitation

GTFS speeds represent **metro schedules**, not **road congestion**.  
This makes the ML model **unsuitable for real traffic prediction** without additional road-based features.

---

## 🤖 Machine Learning (Experimental)

### Model
- `RandomForestClassifier`
- Trained on **GTFS-derived features**

### Purpose
- Academic exploration
- Understanding feature impact
- **Not production traffic prediction**

### Known Issues
- Over-predicts **Heavy traffic**
- Learns unrealistic speed distributions
- Not aligned with real road conditions

### Current Status

- ✅ Trained
- ⚠️ Experimental
- ❌ Not used for live route coloring

---

## 🗺️ Streamlit Dashboard

### Left Panel
- Source & destination input
- Mode of transport (car / bicycle / pedestrian)
- LLM-generated travel advisory

### Right Panel
- Interactive OpenStreetMap view
- Stable route polyline (no blinking)
- Source and destination markers

---

## 🔗 Data Sources

| Component | Source |
|-------|--------|
| Routing | TomTom Routing API |
| Geocoding | TomTom Search API |
| Weather | OpenWeather API |
| Advisory | Groq LLM |
| Map | OpenStreetMap (Folium) |

---

## 📦 Installation & Setup

```bash
# Clone repository
git clone https://github.com/SamIeer/traffic-prediction.git
cd traffic-prediction

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py

---

## Docker

Before building the image, check that Docker is installed and the daemon is running:

```bash
# Check Docker installation
docker --version
# Check Docker daemon (will error if daemon is not running)
docker info
```

You can containerize and deploy the app using Docker. Build the image from the project root and run the container with Streamlit's default port (8501) exposed.

```bash
# Build the Docker image (run from project root)
docker build -t delhi-traffic-app .

# Run the container, mapping Streamlit's port 8501 to your host
docker run --rm -p 8501:8501 delhi-traffic-app

# Optional: run detached
# docker run -d --rm -p 8501:8501 delhi-traffic-app
```

**Notes:**

- Ensure Streamlit inside the container is configured to listen on `0.0.0.0` (not just `localhost`). You can set this via environment variable or Streamlit config: `STREAMLIT_SERVER_ADDRESS=0.0.0.0`.
- Pass secrets (API keys) securely with `--env-file` or `-e` when running the container, or use a secrets manager for production.
- For multi-service setups, see `docker-compose.yml`.

## Project Structure
traffic-prediction/
│── app.py                     # Streamlit application
│── Dataset/
│   ├── raw/
│   ├── processed/
│   └── gtfs_labeled.csv
│
│── ML/
│   ├── train_rf.py
│   ├── create_labels.py
│   ├── traffic_rf_model.pkl
│   └── label_encoder.pkl
│
│── services/
│   ├── tomtom_service.py
│   ├── weather_service.py
│   └── llm_service.py
│
│── Dockerfile
│── requirements.txt
│── README.md
