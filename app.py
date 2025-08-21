import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from geopy.distance import geodesic
import json
from datetime import datetime

# Page config
st.set_page_config(page_title="LocationShare", page_icon="📍", layout="wide")

# Initialize Firebase (if not already initialized)
if not firebase_admin._apps:
    # For Streamlit Cloud, use secrets.toml. For local, use .env or direct input
    try:
        # For Streamlit sharing (secrets)
        firebase_config = st.secrets["firebase"]
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": firebase_config["project_id"],
            "private_key": firebase_config["private_key"].replace('\\n', '\n'),
            "client_email": firebase_config["client_email"]
        })
    except:
        # For local development - manually input credentials
        st.sidebar.info("Enter Firebase credentials")
        project_id = st.sidebar.text_input("Project ID")
        private_key = st.sidebar.text_area("Private Key")
        client_email = st.sidebar.text_input("Client Email")
        
        if project_id and private_key and client_email:
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": project_id,
                "private_key": private_key.replace('\\n', '\n'),
                "client_email": client_email
            })
        else:
            st.warning("Please enter Firebase credentials in the sidebar")
            st.stop()
    
    firebase_admin.initialize_app(cred)

db = firestore.client()

# App title
st.title("📍 Streamlit Location Share")
st.markdown("Share your location with one click!")

# User session ID
if 'user_id' not in st.session_state:
    st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Main columns
col1, col2 = st.columns(2)

with col1:
    st.header("Share Your Location")
    
    if st.button("📍 Share My Location", type="primary"):
        # Get current location (simulated - in production, use JavaScript)
        # Note: Streamlit doesn't directly access geolocation. We'll use input for demo.
        lat = st.number_input("Latitude", value=40.7128, format="%.6f")
        lng = st.number_input("Longitude", value=-74.0060, format="%.6f")
        
        # Save to Firebase
        doc_ref = db.collection('locations').document(st.session_state.user_id)
        doc_ref.set({
            'lat': lat,
            'lng': lng,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'user_agent': 'Streamlit App'
        })
        st.success("Location shared successfully!")
    
    st.divider()
    
    # Manual location input (for demo)
    st.subheader("Manual Location Input")
    with st.form("manual_location"):
        manual_lat = st.number_input("Enter Latitude", value=40.7128, format="%.6f")
        manual_lng = st.number_input("Enter Longitude", value=-74.0060, format="%.6f")
        if st.form_submit_button("Save Manual Location"):
            db.collection('locations').document(st.session_state.user_id).set({
                'lat': manual_lat,
                'lng': manual_lng,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            st.success("Manual location saved!")

with col2:
    st.header("View Shared Locations")
    
    # Get all locations
    try:
        docs = db.collection('locations').stream()
        locations = []
        for doc in docs:
            data = doc.to_dict()
            locations.append({
                'user_id': doc.id,
                'lat': data.get('lat', 0),
                'lng': data.get('lng', 0),
                'timestamp': data.get('timestamp')
            })
        
        if locations:
            st.dataframe(locations, use_container_width=True)
            
            # Calculate distances
            st.subheader("Distance Calculator")
            user_ids = [loc['user_id'] for loc in locations]
            selected_user1 = st.selectbox("Select User 1", user_ids)
            selected_user2 = st.selectbox("Select User 2", user_ids)
            
            if selected_user1 and selected_user2:
                loc1 = next((loc for loc in locations if loc['user_id'] == selected_user1), None)
                loc2 = next((loc for loc in locations if loc['user_id'] == selected_user2), None)
                
                if loc1 and loc2:
                    distance = geodesic(
                        (loc1['lat'], loc1['lng']), 
                        (loc2['lat'], loc2['lng'])
                    ).km
                    
                    st.metric("Distance Between Users", f"{distance:.2f} km")
                    
                    # Show on map
                    st.subheader("Map View")
                    st.map(pd.DataFrame([{
                        'lat': loc1['lat'],
                        'lon': loc1['lng']
                    }, {
                        'lat': loc2['lat'],
                        'lon': loc2['lng']
                    }]))
        else:
            st.info("No locations shared yet. Share your location first!")
            
    except Exception as e:
        st.error(f"Error loading locations: {e}")

# Sidebar info
st.sidebar.header("About")
st.sidebar.info("""
This app allows real-time location sharing using:
- Streamlit for the UI
- Firebase Firestore for data storage
- Geopy for distance calculations
""")

st.sidebar.divider()
st.sidebar.write(f"Your User ID: `{st.session_state.user_id}`")
if st.sidebar.button("Generate New User ID"):
    st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    st.rerun()
