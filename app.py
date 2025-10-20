import streamlit as st
from streamlit_folium import st_folium
import folium
import requests

st.title("🚖 Taxi Fare Predictor")

st.write('click pick-up and drop-off locations!')
# Initialize session state for coordinates
if "pickup" not in st.session_state:
    st.session_state.pickup = None
if "dropoff" not in st.session_state:
    st.session_state.dropoff = None

# Create map centered at NYC
center = [40.7580, -73.9855]
m = folium.Map(location=center, zoom_start=12)

# Add pickup marker if exists
if st.session_state.pickup:
    folium.Marker(
        location=st.session_state.pickup,
        tooltip="Pickup",
        icon=folium.Icon(color="green", icon="taxi", prefix="fa")
    ).add_to(m)

# Add dropoff marker if exists
if st.session_state.dropoff:
    folium.Marker(
        location=st.session_state.dropoff,
        tooltip="Dropoff",
        icon=folium.Icon(color="red", icon="flag", prefix="fa")
    ).add_to(m)

# Add line if both points exist
if st.session_state.pickup and st.session_state.dropoff:
    folium.PolyLine(
        locations=[st.session_state.pickup, st.session_state.dropoff],
        color="blue",
        weight=5,
        opacity=0.7
    ).add_to(m)

# Render map and get click info
map_data = st_folium(m, height=500)

if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    # Decide if pickup or dropoff
    if st.session_state.pickup is None:
        st.session_state.pickup = [lat, lon]
        st.success(f"Pickup set at {lat:.5f}, {lon:.5f}")
    elif st.session_state.dropoff is None:
        st.session_state.dropoff = [lat, lon]
        st.success(f"Dropoff set at {lat:.5f}, {lon:.5f}")
    else:
        # If both exist, overwrite dropoff on subsequent clicks
        st.session_state.dropoff = [lat, lon]
        st.info(f"Dropoff moved to {lat:.5f}, {lon:.5f}")

# Other inputs
pickup_datetime = st.text_input("Pickup datetime (YYYY-MM-DD HH:MM:SS)", "2025-10-20 15:30:00")
passenger_count = st.number_input("Passenger count", min_value=1, max_value=8, value=1)

# Predict button
url = "https://taxifare.lewagon.ai/predict"

if st.button("Predict Fare"):
    if not st.session_state.pickup or not st.session_state.dropoff:
        st.error("Please click on the map to select both pickup and dropoff locations.")
    else:
        params = {
            "pickup_datetime": pickup_datetime,
            "pickup_longitude": st.session_state.pickup[1],
            "pickup_latitude": st.session_state.pickup[0],
            "dropoff_longitude": st.session_state.dropoff[1],
            "dropoff_latitude": st.session_state.dropoff[0],
            "passenger_count": passenger_count
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            fare = response.json().get("fare")
            if fare:
                st.success(f"Predicted Fare: ${fare:.2f}")

                st.balloons()
            else:
                st.warning("Fare not found in API response.")
        else:
            st.error(f"API error: {response.status_code} - {response.text}")
