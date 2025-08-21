import streamlit as st
import json
import requests
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
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown('<h1 class="main-header">📍 Location Share</h1>', unsafe_allow_html=True)
st.markdown("""
<div class="info-box">
    <p>Share your current location with friends and family!</p>
    <p>This app will:</p>
    <ol>
        <li>Request access to your device's location</li>
        <li>Get your current coordinates</li>
        <li>Generate a shareable link with your location</li>
    </ol>
</div>
""", unsafe_allow_html=True)

# JavaScript code to get location
get_location_js = """
<script>
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

function showPosition(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;
    const accuracy = position.coords.accuracy;
    
    // Set values in Streamlit
    window.parent.document.querySelector('input[data-testid="stNumberInput"]').value = latitude;
    window.parent.document.querySelector('input[data-testid="stNumberInput"]').dispatchEvent(new Event('input', {bubbles: true}));
    
    // We'll use a hidden text input to pass all data
    const locationData = JSON.stringify({
        latitude: latitude,
        longitude: longitude,
        accuracy: accuracy,
        timestamp: new Date().toISOString()
    });
    
    const hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.id = 'locationData';
    hiddenInput.value = locationData;
    document.body.appendChild(hiddenInput);
    
    // Trigger Streamlit update
    hiddenInput.dispatchEvent(new Event('input', {bubbles: true}));
}

function showError(error) {
    switch(error.code) {
        case error.PERMISSION_DENIED:
            alert("User denied the request for Geolocation.");
            break;
        case error.POSITION_UNAVAILABLE:
            alert("Location information is unavailable.");
            break;
        case error.TIMEOUT:
            alert("The request to get user location timed out.");
            break;
        case error.UNKNOWN_ERROR:
            alert("An unknown error occurred.");
            break;
    }
}
</script>
"""

# Display the JavaScript
st.components.v1.html(get_location_js, height=0)

# Button to get location
st.markdown("### Step 1: Get Your Location")
if st.button("📍 Get My Location", key="get_location"):
    st.components.v1.html(
        "<script>getLocation()</script>",
        height=0
    )
    st.info("Please allow location access in your browser when prompted.")

# Input for location data (hidden by default)
location_data = st.text_input("Location Data", key="location_data", type="default", label_visibility="collapsed")

# Process location data if available
if location_data:
    try:
        location = json.loads(location_data)
        st.session_state['location'] = location
        
        st.markdown("### Step 2: Your Location Details")
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
                <li>Generating a Google Maps link below</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate Google Maps link
        maps_link = f"https://www.google.com/maps?q={location['latitude']},{location['longitude']}"
        st.markdown(f"**Google Maps Link:** [Click to open]({maps_link})")
        
        # Copy to clipboard functionality
        st.markdown(f"""
        <script>
            function copyToClipboard() {{
                navigator.clipboard.writeText("{maps_link}");
                alert("Google Maps link copied to clipboard!");
            }}
        </script>
        <button onclick="copyToClipboard()">Copy Google Maps Link</button>
        """, unsafe_allow_html=True)
        
    except json.JSONDecodeError:
        st.error("Failed to parse location data.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center;">
    <p>Built with Streamlit · Your location data is not stored on any server</p>
</div>
""", unsafe_allow_html=True)
