import streamlit as st
import json
import pandas as pd
from datetime import datetime
import pytz

# Set page configuration
st.set_page_config(
    page_title="Location Share",
    page_icon="📍",
    layout="centered"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
    }
    .stButton button {
        background-color: #1f77b4;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        cursor: pointer;
    }
    .stButton button:hover {
        background-color: #ff7f0e;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-radius: 0.5rem;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
    .location-data {
        font-family: monospace;
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        overflow-x: auto;
    }
    .manual-input {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ffeeba;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown('<h1 class="main-header">📍 Location Share</h1>', unsafe_allow_html=True)
st.markdown("""
<div class="info-box">
    <p>Share your current location with friends and family!</p>
    <p>This app will:</p>
    <ol>
        <li>Help you get your current coordinates</li>
        <li>Display your location on a map</li>
        <li>Generate a shareable link with your location</li>
    </ol>
    <p><strong>Note:</strong> For the best experience, use HTTPS and allow location access when prompted.</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'location' not in st.session_state:
    st.session_state.location = None
if 'manual_coords' not in st.session_state:
    st.session_state.manual_coords = None

# Function to create a Google Maps link
def create_maps_link(lat, lng):
    return f"https://www.google.com/maps?q={lat},{lng}"

# Option 1: Manual coordinate input
st.markdown("### Option 1: Enter Coordinates Manually")
st.markdown('<div class="manual-input">', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    manual_lat = st.number_input("Latitude", value=40.7128, format="%.6f")
with col2:
    manual_lng = st.number_input("Longitude", value=-74.0060, format="%.6f")

if st.button("Use These Coordinates", key="manual_coords"):
    st.session_state.manual_coords = {
        "latitude": manual_lat,
        "longitude": manual_lng,
        "accuracy": 0,
        "timestamp": datetime.now().isoformat()
    }
    st.session_state.location = st.session_state.manual_coords
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Option 2: Get location via browser (using HTML injection)
st.markdown("### Option 2: Get Location via Browser")
st.markdown("""
<div class="info-box">
    <p>Click the button below to get your location. Your browser will ask for permission to access your location.</p>
    <p><strong>Note:</strong> This works best on HTTPS connections and may not work on all browsers.</p>
</div>
""", unsafe_allow_html=True)

# HTML and JavaScript for geolocation
geolocation_html = """
<div>
    <button onclick="getLocation()" style="background-color: #1f77b4; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; cursor: pointer;">
        📍 Get My Location
    </button>
    <p id="demo" style="margin-top: 1rem;"></p>
</div>

<script>
var x = document.getElementById("demo");

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError, {enableHighAccuracy: true, timeout: 10000});
    } else {
        x.innerHTML = "Geolocation is not supported by this browser.";
    }
}

function showPosition(position) {
    x.innerHTML = "Location received!";
    
    // Create a form and submit the coordinates
    var form = document.createElement("form");
    form.method = "POST";
    form.action = window.location.href;
    
    var latInput = document.createElement("input");
    latInput.type = "hidden";
    latInput.name = "latitude";
    latInput.value = position.coords.latitude;
    form.appendChild(latInput);
    
    var lngInput = document.createElement("input");
    lngInput.type = "hidden";
    lngInput.name = "longitude";
    lngInput.value = position.coords.longitude;
    form.appendChild(lngInput);
    
    var accInput = document.createElement("input");
    accInput.type = "hidden";
    accInput.name = "accuracy";
    accInput.value = position.coords.accuracy;
    form.appendChild(accInput);
    
    document.body.appendChild(form);
    form.submit();
}

function showError(error) {
    switch(error.code) {
        case error.PERMISSION_DENIED:
            x.innerHTML = "User denied the request for Geolocation.";
            break;
        case error.POSITION_UNAVAILABLE:
            x.innerHTML = "Location information is unavailable.";
            break;
        case error.TIMEOUT:
            x.innerHTML = "The request to get user location timed out.";
            break;
        case error.UNKNOWN_ERROR:
            x.innerHTML = "An unknown error occurred.";
            break;
    }
}
</script>
"""

# Display the geolocation HTML
st.components.v1.html(geolocation_html, height=200)

# Check if coordinates were submitted via form
if st.query_params:
    latitude = st.query_params.get("latitude", [None])[0]
    longitude = st.query_params.get("longitude", [None])[0]
    accuracy = st.query_params.get("accuracy", [None])[0]
    
    if latitude and longitude:
        st.session_state.location = {
            "latitude": float(latitude),
            "longitude": float(longitude),
            "accuracy": float(accuracy) if accuracy else 0,
            "timestamp": datetime.now().isoformat()
        }
        st.rerun()

# Display location if available
if st.session_state.location:
    location = st.session_state.location
    
    st.markdown("### 📍 Your Location Details")
    st.markdown(f"""
    <div class="location-data">
        <p><strong>Latitude:</strong> {location['latitude']}</p>
        <p><strong>Longitude:</strong> {location['longitude']}</p>
        <p><strong>Accuracy:</strong> ±{location['accuracy']} meters</p>
        <p><strong>Timestamp:</strong> {datetime.fromisoformat(location['timestamp'].replace('Z', '+00:00')).astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show on map
    st.markdown("### 📍 Your Location on Map")
    st.map(pd.DataFrame({
        'lat': [location['latitude']],
        'lon': [location['longitude']]
    }), zoom=14)
    
    st.markdown("### Step 3: Share Your Location")
    st.markdown("""
    <div class="info-box">
        <p>You can share your location by:</p>
        <ol>
            <li>Copying the coordinates above</li>
            <li>Taking a screenshot of the map</li>
            <li>Using the Google Maps link below</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # Generate Google Maps link
    maps_link = create_maps_link(location['latitude'], location['longitude'])
    st.markdown(f"**Google Maps Link:** [Click to open]({maps_link})")
    
    # Copy to clipboard functionality
    st.markdown(f"""
    <div>
        <button onclick="navigator.clipboard.writeText('{maps_link}'); alert('Google Maps link copied to clipboard!');" 
                style="background-color: #1f77b4; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; cursor: pointer; margin-top: 1rem;">
            Copy Google Maps Link
        </button>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center;">
    <p>Built with Streamlit · Your location data is not stored on any server</p>
    <p>If browser location doesn't work, use the manual input option above</p>
</div>
""", unsafe_allow_html=True)
