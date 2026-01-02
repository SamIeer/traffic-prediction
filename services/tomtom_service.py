import os
import requests
from dotenv import load_dotenv
from urllib.parse import quote

# --------------------------------------------------
# ENV SETUP
# --------------------------------------------------
load_dotenv("secrets.env")
TOMTOM_KEY = os.getenv("TOMTOM_API_KEY")

if not TOMTOM_KEY:
    raise RuntimeError("❌ TOMTOM_API_KEY not found in secrets.env")


# --------------------------------------------------
# AUTOCOMPLETE (Google-Maps-like suggestions)
# --------------------------------------------------
def autocomplete_places(query: str, country="IN", limit=5):
    """
    Returns list of place suggestions:
    [{label, lat, lon}]
    """
    if not query or len(query) < 2:
        return []

    url = "https://api.tomtom.com/search/2/search.json"
    params = {
        "key": TOMTOM_KEY,
        "query": query,
        "limit": limit,
        "countrySet": country,
        "typeahead": True
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        results = []

        for item in r.json().get("results", []):
            addr = item.get("address", {})
            pos = item.get("position", {})

            if "lat" in pos and "lon" in pos:
                results.append({
                    "label": addr.get("freeformAddress", "Unknown"),
                    "lat": pos["lat"],
                    "lon": pos["lon"]
                })

        return results

    except requests.RequestException:
        return []


# --------------------------------------------------
# GEOCODING (fallback if autocomplete not used)
# --------------------------------------------------
def geocode_tomtom(query: str, country="IN"):
    """
    Convert place name → (lat, lon)
    """
    url = f"https://api.tomtom.com/search/2/geocode/{quote(query)}.json"
    params = {
        "key": TOMTOM_KEY,
        "limit": 1,
        "countrySet": country
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        results = r.json().get("results", [])

        if results:
            pos = results[0]["position"]
            return float(pos["lat"]), float(pos["lon"])

    except requests.RequestException:
        pass

    return None


# --------------------------------------------------
# ROUTING
# --------------------------------------------------
def route_tomtom(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    mode="car",
    traffic=True
):
    """
    Returns route summary + polyline points
    """
    coord_str = f"{start_lat},{start_lon}:{end_lat},{end_lon}"
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{coord_str}/json"

    params = {
        "key": TOMTOM_KEY,
        "travelMode": mode,
        "traffic": str(traffic).lower(),
        "routeRepresentation": "polyline"
    }

    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        routes = r.json().get("routes", [])

        if not routes:
            return None

        route = routes[0]
        summary = route.get("summary", {})

        points = []
        for leg in route.get("legs", []):
            for p in leg.get("points", []):
                points.append((p["latitude"], p["longitude"]))

        return {
            "points": points,
            "length_m": summary.get("lengthInMeters"),
            "time_s": summary.get("travelTimeInSeconds"),
            "delay_s": summary.get("trafficDelayInSeconds", 0),
            "departureTime": summary.get("departureTime"),
            "arrivalTime": summary.get("arrivalTime")
        }

    except requests.RequestException:
        return None
