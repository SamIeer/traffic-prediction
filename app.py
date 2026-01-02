# app.py
import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime

from services.tomtom_service import geocode_tomtom, route_tomtom
from services.weather_service import weather_onecall
from services.llm_service import ask_llm


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Delhi Traffic Analysis",
    layout="wide"
)

st.title("🚦 Delhi Traffic Analysis (Stable & Honest)")


# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def km(meters):
    if not meters:
        return "—"
    return f"{meters / 1000:.1f} km"


def human_eta(seconds):
    if not seconds or seconds <= 0:
        return "—"
    mins = int(seconds / 60)
    return f"{mins} min" if mins < 60 else f"{mins//60} h {mins%60} min"


def draw_route(fmap, points):
    """
    Draw a SINGLE polyline
    (No blinking, no mutation)
    """
    folium.PolyLine(
        locations=points,
        color="#1E90FF",   # Google-like blue
        weight=6,
        opacity=0.9
    ).add_to(fmap)


# --------------------------------------------------
# SESSION STATE (DATA ONLY)
# --------------------------------------------------
for key in [
    "src_coords",
    "dst_coords",
    "route_points",
    "route_summary",
    "advisory_text"
]:
    if key not in st.session_state:
        st.session_state[key] = None


# --------------------------------------------------
# UI LAYOUT
# --------------------------------------------------
left, right = st.columns([1, 1], gap="large")

# ================= LEFT PANEL ======================
with left:
    st.subheader("📍 Plan Your Trip")

    src_text = st.text_input(
        "Source (example format)",
        "Connaught Place, New Delhi"
    )

    dst_text = st.text_input(
        "Destination (example format)",
        "Indira Gandhi International Airport, New Delhi"
    )

    mode = st.selectbox(
        "Mode of Transport",
        ["car", "bicycle", "pedestrian"]
    )

    use_traffic = st.checkbox("Use live traffic (TomTom)", value=True)

    calculate = st.button("🚀 Calculate Route", use_container_width=True)

    st.divider()

    st.subheader("🧠 Traffic Analysis (Honest Mode)")
    st.info(
        """
        ⚠️ Traffic ML is currently **experimental**.

        - Uses TomTom live route delay
        - NOT predicting exact congestion colors
        - Designed for research & future improvements
        """
    )

    if st.session_state.advisory_text:
        st.subheader("🤖 Travel Advisory")
        st.write(st.session_state.advisory_text)


# ================= RIGHT PANEL =====================
with right:
    st.subheader("🗺️ Route Map")

    if st.session_state.route_points:
        mid = st.session_state.route_points[
            len(st.session_state.route_points) // 2
        ]

        fmap = folium.Map(
            location=mid,
            zoom_start=12,
            tiles="OpenStreetMap"
        )

        folium.Marker(
            st.session_state.src_coords,
            popup="Source",
            icon=folium.Icon(color="green")
        ).add_to(fmap)

        folium.Marker(
            st.session_state.dst_coords,
            popup="Destination",
            icon=folium.Icon(color="red")
        ).add_to(fmap)

        draw_route(fmap, st.session_state.route_points)

        st_folium(fmap, height=650, width=750)
    else:
        st.info("Route map will appear here after calculation.")


# --------------------------------------------------
# ACTION (ON BUTTON CLICK ONLY)
# --------------------------------------------------
if calculate:
    with st.spinner("Calculating route using TomTom..."):
        src = geocode_tomtom(src_text)
        dst = geocode_tomtom(dst_text)

        if not src or not dst:
            st.error("❌ Unable to geocode one of the locations.")
        else:
            route = route_tomtom(
                src[0], src[1],
                dst[0], dst[1],
                mode=mode,
                traffic=use_traffic
            )

            if not route or not route.get("points"):
                st.error("❌ Route not found.")
            else:
                # ---------------- SAVE DATA ONLY ----------------
                st.session_state.src_coords = src
                st.session_state.dst_coords = dst
                st.session_state.route_points = route["points"]

                st.session_state.route_summary = {
                    "distance": km(route["length_m"]),
                    "eta": human_eta(route["time_s"]),
                    "delay": human_eta(route.get("delay_s", 0))
                }

                # ---------------- WEATHER ----------------
                wx = weather_onecall(dst[0], dst[1])
                weather_desc = (
                    wx["weather"][0]["description"] if wx else "—"
                )
                temp = wx["main"]["temp"] if wx else "—"

                # ---------------- ADVISORY (LLM) ----------------
                st.session_state.advisory_text = ask_llm(
                    f"""
Trip Summary:
From: {src_text}
To: {dst_text}

Distance: {km(route["length_m"])}
ETA: {human_eta(route["time_s"])}
Traffic Delay: {human_eta(route.get("delay_s", 0))}

Weather at destination:
{weather_desc}, {temp}°C

Give short, safe travel advice.
"""
                )
