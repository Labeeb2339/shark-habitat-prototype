#!/usr/bin/env python3
"""
Shark Habitat Prediction Web Application
Interactive UI for visualizing shark habitat suitability data
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, date
import json
import os
from automatic_nasa_framework import AutomaticNASAFramework
# from shark_analysis_visualization import HabitatAnalyzer, ReportGenerator

# Configure Streamlit page
st.set_page_config(
    page_title="🦈 Shark Habitat Predictor",
    page_icon="🦈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .species-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }

    /* Fix dropdown text visibility */
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* Fix dropdown options */
    .stSelectbox > div > div > div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* Fix dropdown menu */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* Fix dropdown text */
    div[data-baseweb="select"] > div > div {
        color: #000000 !important;
    }

    /* Fix dropdown options list */
    ul[role="listbox"] {
        background-color: #ffffff !important;
    }

    ul[role="listbox"] li {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    ul[role="listbox"] li:hover {
        background-color: #e6f3ff !important;
        color: #000000 !important;
    }

    /* Additional fixes for Streamlit selectbox */
    .stSelectbox label {
        color: #000000 !important;
        font-weight: bold !important;
    }

    /* Force dark text in all selectbox elements */
    .stSelectbox div[data-testid="stSelectbox"] > div > div {
        color: #000000 !important;
        background-color: #ffffff !important;
    }

    /* Fix for the actual dropdown text */
    .stSelectbox div[role="button"] {
        color: #000000 !important;
        background-color: #ffffff !important;
    }

    /* Ensure dropdown arrow is visible */
    .stSelectbox svg {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

def load_species_data():
    """Load species information for the UI - All 24 species"""
    return {
        'great_white': {
            'name': 'Great White Shark',
            'scientific': 'Carcharodon carcharias',
            'optimal_temp': 18,
            'temp_range': '12-24°C',
            'depth_range': '0-250m',
            'habitat': 'Temperate coastal waters',
            'emoji': '🦈',
            'hunting': 'Ambush predator',
            'migration': 'High'
        },
        'tiger_shark': {
            'name': 'Tiger Shark',
            'scientific': 'Galeocerdo cuvier',
            'optimal_temp': 25,
            'temp_range': '20-30°C',
            'depth_range': '0-350m',
            'habitat': 'Tropical coastal waters',
            'emoji': '🐅',
            'hunting': 'Generalist predator',
            'migration': 'Moderate'
        },
        'bull_shark': {
            'name': 'Bull Shark',
            'scientific': 'Carcharhinus leucas',
            'optimal_temp': 27,
            'temp_range': '22-32°C',
            'depth_range': '0-150m',
            'habitat': 'Estuarine and coastal waters',
            'emoji': '🐂',
            'hunting': 'Opportunistic predator',
            'migration': 'Low'
        },
        'hammerhead': {
            'name': 'Great Hammerhead Shark',
            'scientific': 'Sphyrna mokarran',
            'optimal_temp': 24,
            'temp_range': '21-27°C',
            'depth_range': '0-300m',
            'habitat': 'Tropical pelagic waters',
            'emoji': '🔨',
            'hunting': 'Ray specialist',
            'migration': 'High'
        },
        'mako': {
            'name': 'Shortfin Mako Shark',
            'scientific': 'Isurus oxyrinchus',
            'optimal_temp': 20,
            'temp_range': '15-25°C',
            'depth_range': '0-500m',
            'habitat': 'Open ocean (pelagic)',
            'emoji': '⚡',
            'hunting': 'High-speed predator',
            'migration': 'Very High'
        },
        'blue_shark': {
            'name': 'Blue Shark',
            'scientific': 'Prionace glauca',
            'optimal_temp': 16,
            'temp_range': '10-22°C',
            'depth_range': '0-400m',
            'habitat': 'Open ocean',
            'emoji': '🌊',
            'hunting': 'Opportunistic pelagic',
            'migration': 'Extremely High'
        },
        'whale_shark': {
            'name': 'Whale Shark',
            'scientific': 'Rhincodon typus',
            'optimal_temp': 26,
            'temp_range': '21-30°C',
            'depth_range': '0-200m',
            'habitat': 'Tropical surface waters',
            'emoji': '🐋',
            'hunting': 'Filter feeder',
            'migration': 'High'
        },
        'basking_shark': {
            'name': 'Basking Shark',
            'scientific': 'Cetorhinus maximus',
            'optimal_temp': 14,
            'temp_range': '8-20°C',
            'depth_range': '0-200m',
            'habitat': 'Temperate surface waters',
            'emoji': '🦈',
            'hunting': 'Filter feeder',
            'migration': 'Very High'
        },
        'thresher_shark': {
            'name': 'Common Thresher Shark',
            'scientific': 'Alopias vulpinus',
            'optimal_temp': 19,
            'temp_range': '14-24°C',
            'depth_range': '0-500m',
            'habitat': 'Temperate pelagic waters',
            'emoji': '🌊',
            'hunting': 'Tail stunning',
            'migration': 'High'
        },
        'nurse_shark': {
            'name': 'Nurse Shark',
            'scientific': 'Ginglymostoma cirratum',
            'optimal_temp': 26,
            'temp_range': '22-30°C',
            'depth_range': '0-75m',
            'habitat': 'Tropical reef waters',
            'emoji': '😴',
            'hunting': 'Suction feeder',
            'migration': 'Very Low'
        },
        'reef_shark': {
            'name': 'Caribbean Reef Shark',
            'scientific': 'Carcharhinus perezi',
            'optimal_temp': 27,
            'temp_range': '24-30°C',
            'depth_range': '0-100m',
            'habitat': 'Coral reef waters',
            'emoji': '🏝️',
            'hunting': 'Reef predator',
            'migration': 'Low'
        },
        'lemon_shark': {
            'name': 'Lemon Shark',
            'scientific': 'Negaprion brevirostris',
            'optimal_temp': 26,
            'temp_range': '20-30°C',
            'depth_range': '0-90m',
            'habitat': 'Mangrove coastal waters',
            'emoji': '🍋',
            'hunting': 'Active predator',
            'migration': 'Moderate'
        },
        'blacktip_shark': {
            'name': 'Blacktip Shark',
            'scientific': 'Carcharhinus limbatus',
            'optimal_temp': 25,
            'temp_range': '20-30°C',
            'depth_range': '0-100m',
            'habitat': 'Shallow coastal waters',
            'emoji': '⚫',
            'hunting': 'Fast pursuit',
            'migration': 'High'
        },
        'sandbar_shark': {
            'name': 'Sandbar Shark',
            'scientific': 'Carcharhinus plumbeus',
            'optimal_temp': 22,
            'temp_range': '16-28°C',
            'depth_range': '20-280m',
            'habitat': 'Continental shelf',
            'emoji': '🏖️',
            'hunting': 'Bottom predator',
            'migration': 'High'
        },
        'spinner_shark': {
            'name': 'Spinner Shark',
            'scientific': 'Carcharhinus brevipinna',
            'optimal_temp': 24,
            'temp_range': '19-29°C',
            'depth_range': '0-100m',
            'habitat': 'Warm coastal waters',
            'emoji': '🌀',
            'hunting': 'Spinning attack',
            'migration': 'High'
        },
        'dusky_shark': {
            'name': 'Dusky Shark',
            'scientific': 'Carcharhinus obscurus',
            'optimal_temp': 20,
            'temp_range': '15-28°C',
            'depth_range': '0-400m',
            'habitat': 'Temperate coastal waters',
            'emoji': '🌫️',
            'hunting': 'Pursuit predator',
            'migration': 'Very High'
        },
        'silky_shark': {
            'name': 'Silky Shark',
            'scientific': 'Carcharhinus falciformis',
            'optimal_temp': 24,
            'temp_range': '20-28°C',
            'depth_range': '0-500m',
            'habitat': 'Tropical pelagic waters',
            'emoji': '✨',
            'hunting': 'Pelagic predator',
            'migration': 'Very High'
        },
        'porbeagle_shark': {
            'name': 'Porbeagle Shark',
            'scientific': 'Lamna nasus',
            'optimal_temp': 12,
            'temp_range': '5-18°C',
            'depth_range': '0-700m',
            'habitat': 'Cold pelagic waters',
            'emoji': '❄️',
            'hunting': 'Endothermic predator',
            'migration': 'Very High'
        },

        # ADDITIONAL MAJOR SPECIES (6 new species)
        'longfin_mako': {
            'name': 'Longfin Mako Shark',
            'scientific': 'Isurus paucus',
            'optimal_temp': 18,
            'temp_range': '13-23°C',
            'depth_range': '0-220m',
            'habitat': 'Tropical open ocean',
            'emoji': '⚡',
            'hunting': 'Endothermic predator',
            'migration': 'Very High'
        },
        'salmon_shark': {
            'name': 'Salmon Shark',
            'scientific': 'Lamna ditropis',
            'optimal_temp': 10,
            'temp_range': '5-15°C',
            'depth_range': '0-255m',
            'habitat': 'North Pacific cold waters',
            'emoji': '🐟',
            'hunting': 'Endothermic predator',
            'migration': 'High'
        },
        'sand_tiger': {
            'name': 'Sand Tiger Shark',
            'scientific': 'Carcharias taurus',
            'optimal_temp': 20,
            'temp_range': '15-25°C',
            'depth_range': '0-190m',
            'habitat': 'Temperate coastal waters',
            'emoji': '🏜️',
            'hunting': 'Ambush predator',
            'migration': 'Moderate'
        },
        'scalloped_hammerhead': {
            'name': 'Scalloped Hammerhead',
            'scientific': 'Sphyrna lewini',
            'optimal_temp': 23,
            'temp_range': '18-28°C',
            'depth_range': '0-275m',
            'habitat': 'Tropical coastal waters',
            'emoji': '🔨',
            'hunting': 'Electroreception predator',
            'migration': 'Very High'
        },
        'smooth_hammerhead': {
            'name': 'Smooth Hammerhead',
            'scientific': 'Sphyrna zygaena',
            'optimal_temp': 20,
            'temp_range': '15-25°C',
            'depth_range': '0-200m',
            'habitat': 'Temperate coastal waters',
            'emoji': '🔨',
            'hunting': 'Electroreception predator',
            'migration': 'High'
        },
        'bonnethead_shark': {
            'name': 'Bonnethead Shark',
            'scientific': 'Sphyrna tiburo',
            'optimal_temp': 25,
            'temp_range': '20-30°C',
            'depth_range': '0-25m',
            'habitat': 'Shallow warm waters',
            'emoji': '👒',
            'hunting': 'Benthic forager',
            'migration': 'Low'
        }
    }

def create_habitat_map(results, species_info):
    """Create an interactive habitat suitability map"""
    hsi_grid = results['hsi']
    lats = results.get('latitudes', np.linspace(32, 42, len(hsi_grid)))
    lons = results.get('longitudes', np.linspace(-125, -115, len(hsi_grid[0])))
    
    # Create meshgrid for plotting
    lon_grid, lat_grid = np.meshgrid(lons, lats)
    
    # Flatten arrays for plotting
    lat_flat = lat_grid.flatten()
    lon_flat = lon_grid.flatten()
    hsi_flat = np.array(hsi_grid).flatten()
    
    # Create DataFrame
    df = pd.DataFrame({
        'Latitude': lat_flat,
        'Longitude': lon_flat,
        'HSI': hsi_flat,
        'Quality': ['Excellent' if h > 0.8 else 'Good' if h > 0.6 else 'Moderate' if h > 0.4 else 'Poor' if h > 0.2 else 'Unsuitable' for h in hsi_flat]
    })
    
    # Create the map
    fig = px.scatter_mapbox(
        df, 
        lat="Latitude", 
        lon="Longitude", 
        color="HSI",
        size="HSI",
        hover_data=["Quality"],
        color_continuous_scale="Viridis",
        size_max=15,
        zoom=6,
        title=f"{species_info['emoji']} {species_info['name']} Habitat Suitability"
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        height=600,
        title_font_size=20
    )
    
    return fig

def create_hsi_distribution(results):
    """Create HSI distribution histogram"""
    hsi_flat = np.array(results['hsi']).flatten()
    
    fig = px.histogram(
        x=hsi_flat,
        nbins=30,
        title="Habitat Suitability Index Distribution",
        labels={'x': 'HSI Value', 'y': 'Frequency'},
        color_discrete_sequence=['#1f77b4']
    )
    
    fig.add_vline(x=np.mean(hsi_flat), line_dash="dash", line_color="red", 
                  annotation_text=f"Mean: {np.mean(hsi_flat):.3f}")
    
    return fig

def create_quality_pie_chart(results):
    """Create habitat quality distribution pie chart"""
    hsi_flat = np.array(results['hsi']).flatten()
    
    excellent = np.sum(hsi_flat > 0.8)
    good = np.sum((hsi_flat > 0.6) & (hsi_flat <= 0.8))
    moderate = np.sum((hsi_flat > 0.4) & (hsi_flat <= 0.6))
    poor = np.sum((hsi_flat > 0.2) & (hsi_flat <= 0.4))
    unsuitable = np.sum(hsi_flat <= 0.2)
    
    labels = ['Excellent', 'Good', 'Moderate', 'Poor', 'Unsuitable']
    values = [excellent, good, moderate, poor, unsuitable]
    colors = ['#2E8B57', '#32CD32', '#FFD700', '#FF8C00', '#DC143C']
    
    fig = px.pie(
        values=values,
        names=labels,
        title="Habitat Quality Distribution",
        color_discrete_sequence=colors
    )
    
    return fig

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">🦈 Shark Habitat Suitability Explorer</h1>', unsafe_allow_html=True)
    st.markdown("**An educational prototype for exploring heuristic habitat scores**")
    st.info(
        "Evidence boundary: generated environmental layers are demo inputs, "
        "not satellite measurements, live shark locations, or validated ecology."
    )
    
    # Sidebar for controls
    st.sidebar.header("🎛️ Analysis Controls")
    
    # Species selection with better visibility
    species_data = load_species_data()
    species_options = {f"{info['emoji']} {info['name']}": key for key, info in species_data.items()}

    # Add custom styling for the selectbox
    st.sidebar.markdown("**🦈 Select Shark Species:**")
    selected_species_display = st.sidebar.selectbox(
        "Choose species",
        list(species_options.keys()),
        label_visibility="collapsed"
    )
    selected_species = species_options[selected_species_display]
    species_info = species_data[selected_species]
    
    # Study area controls - User-friendly version
    st.sidebar.subheader("📍 Study Area")

    # Preset locations for easy selection
    preset_locations = {
        "🌊 California Coast (Default)": {"lat_min": 32.0, "lat_max": 42.0, "lon_min": -125.0, "lon_max": -115.0, "description": "Great White shark hotspot"},
        "🏝️ Florida Keys": {"lat_min": 24.0, "lat_max": 26.0, "lon_min": -82.0, "lon_max": -80.0, "description": "Tiger & Bull shark habitat"},
        "🦘 Great Barrier Reef": {"lat_min": -24.0, "lat_max": -10.0, "lon_min": 142.0, "lon_max": 154.0, "description": "Diverse shark species"},
        "🇿🇦 South Africa Coast": {"lat_min": -35.0, "lat_max": -30.0, "lon_min": 15.0, "lon_max": 32.0, "description": "Great White aggregation sites"},
        "🌺 Hawaiian Islands": {"lat_min": 18.0, "lat_max": 22.5, "lon_min": -161.0, "lon_max": -154.0, "description": "Tiger shark territory"},
        "🏖️ East Coast USA": {"lat_min": 25.0, "lat_max": 45.0, "lon_min": -85.0, "lon_max": -65.0, "description": "Seasonal shark migrations"},
        "🌴 Caribbean Sea": {"lat_min": 10.0, "lat_max": 27.0, "lon_min": -85.0, "lon_max": -60.0, "description": "Tropical shark species"},
        "🇲🇽 Mexico Pacific": {"lat_min": 14.0, "lat_max": 32.0, "lon_min": -118.0, "lon_max": -105.0, "description": "Diverse marine ecosystems"},
        "🎯 Custom Location": {"lat_min": 32.0, "lat_max": 42.0, "lon_min": -125.0, "lon_max": -115.0, "description": "Set your own coordinates"}
    }

    # Location selector
    selected_location = st.sidebar.selectbox(
        "Choose a study location:",
        list(preset_locations.keys()),
        help="Select a preset location or choose 'Custom Location' to set your own coordinates"
    )

    # Show description of selected location
    location_info = preset_locations[selected_location]
    st.sidebar.info(f"📋 **{selected_location.split(' ', 1)[1]}**\n\n{location_info['description']}")

    # Coordinates input (show advanced controls if custom or if user wants to modify)
    if selected_location == "🎯 Custom Location":
        show_coords = True
    else:
        show_coords = st.sidebar.checkbox("🔧 Modify coordinates", help="Check this to fine-tune the selected location")

    if show_coords:
        st.sidebar.markdown("**🗺️ Coordinate Settings:**")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            lat_min = st.number_input("Min Latitude", value=location_info["lat_min"], step=0.1, format="%.1f")
            lon_min = st.number_input("Min Longitude", value=location_info["lon_min"], step=0.1, format="%.1f")
        with col2:
            lat_max = st.number_input("Max Latitude", value=location_info["lat_max"], step=0.1, format="%.1f")
            lon_max = st.number_input("Max Longitude", value=location_info["lon_max"], step=0.1, format="%.1f")
    else:
        # Use preset coordinates
        lat_min = location_info["lat_min"]
        lat_max = location_info["lat_max"]
        lon_min = location_info["lon_min"]
        lon_max = location_info["lon_max"]

    # Show a helpful coordinate summary
    center_lat = (lat_min + lat_max) / 2
    center_lon = (lon_min + lon_max) / 2
    area_width = abs(lon_max - lon_min)
    area_height = abs(lat_max - lat_min)

    st.sidebar.markdown(f"""
    **📊 Study Area Summary:**
    - **Center**: {center_lat:.1f}°, {center_lon:.1f}°
    - **Size**: {area_width:.1f}° × {area_height:.1f}°
    - **Area**: ~{int(area_width * area_height * 12100)} km²
    """)

    # Add a helpful tip
    if selected_location == "🎯 Custom Location":
        st.sidebar.markdown("""
        **💡 Tips for Custom Locations:**
        - Use Google Maps to find coordinates
        - Right-click → copy coordinates
        - Positive lat = North, Negative = South
        - Positive lon = East, Negative = West
        """)

    # Quick location finder
    with st.sidebar.expander("🔍 Find Coordinates for Any Location"):
        st.markdown("""
        **Quick Coordinate Finder:**

        1. **Google Maps**: Right-click → copy coordinates
        2. **GPS Coordinates**: [gps-coordinates.org](https://gps-coordinates.org/)
        3. **LatLong**: [latlong.net](https://www.latlong.net/)

        **Popular Shark Locations:**
        - **Guadalupe Island**: 29.0°N, -118.3°W
        - **Farallon Islands**: 37.7°N, -123.0°W
        - **Seal Island, SA**: -34.1°S, 18.6°E
        - **Neptune Islands**: -35.3°S, 136.1°E
        - **Tiger Beach, Bahamas**: 26.7°N, -78.9°W
        """)

    # Validation
    coords_valid = True
    if lat_min >= lat_max:
        st.sidebar.error("❌ Min Latitude must be less than Max Latitude")
        coords_valid = False
    if lon_min >= lon_max:
        st.sidebar.error("❌ Min Longitude must be less than Max Longitude")
        coords_valid = False
    if abs(lat_max - lat_min) > 50 or abs(lon_max - lon_min) > 50:
        st.sidebar.warning("⚠️ Large study area may take longer to process")

    # Show study area preview map
    if coords_valid and st.sidebar.checkbox("🗺️ Preview Study Area", help="Show your selected area on a map"):
        preview_df = pd.DataFrame({
            'lat': [center_lat],
            'lon': [center_lon],
            'location': [selected_location.split(' ', 1)[1]]
        })

        preview_fig = px.scatter_mapbox(
            preview_df,
            lat="lat",
            lon="lon",
            hover_name="location",
            zoom=3,
            height=300,
            mapbox_style="open-street-map"
        )

        # Add study area rectangle
        preview_fig.add_shape(
            type="rect",
            x0=lon_min, y0=lat_min,
            x1=lon_max, y1=lat_max,
            line=dict(color="red", width=2),
            fillcolor="rgba(255,0,0,0.1)"
        )

        st.sidebar.plotly_chart(preview_fig, use_container_width=True)
    
    # Date range
    st.sidebar.subheader("📅 Time Period")
    start_date = st.sidebar.date_input("Start Date", value=date(2024, 1, 1))
    end_date = st.sidebar.date_input("End Date", value=date(2024, 1, 31))
    
    # Analysis button
    run_analysis = st.sidebar.button("🚀 Run Analysis", type="primary")
    
    # Species information card
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    <div class="species-card">
        <h3>{species_info['emoji']} {species_info['name']}</h3>
        <p><strong>Scientific:</strong> <em>{species_info['scientific']}</em></p>
        <p><strong>Optimal Temp:</strong> {species_info['optimal_temp']}°C</p>
        <p><strong>Temp Range:</strong> {species_info['temp_range']}</p>
        <p><strong>Depth Range:</strong> {species_info['depth_range']}</p>
        <p><strong>Habitat:</strong> {species_info['habitat']}</p>
        <p><strong>Hunting Style:</strong> {species_info['hunting']}</p>
        <p><strong>Migration:</strong> {species_info['migration']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content area
    if run_analysis:
        with st.spinner(f"🔄 Analyzing {species_info['name']} habitat..."):
            try:
                # Initialize NASA framework with error handling
                st.info(f"🔄 Initializing framework for {selected_species}...")

                # Import and initialize framework
                try:
                    framework = AutomaticNASAFramework(species=selected_species)
                    st.success(f"✅ Framework initialized for {framework.shark_params['name']}")
                except Exception as init_error:
                    st.error(f"❌ Framework initialization failed: {init_error}")
                    # Try with default species as fallback
                    st.info("🔄 Trying with default species...")
                    framework = AutomaticNASAFramework()
                    framework.set_species(selected_species)
                    st.success(f"✅ Framework initialized for {framework.shark_params['name']}")

                # Define study area
                study_area = {
                    'name': f'{selected_location} - {species_info["name"]} Analysis',
                    'bounds': [lon_min, lat_min, lon_max, lat_max],
                    'description': f'Habitat analysis for {species_info["name"]}'
                }

                # Date range
                date_range = [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]

                # Get environmental data
                environmental_data, real_data = framework.auto_download_nasa_data(study_area, date_range)

                # Predict habitat
                results = framework.advanced_habitat_prediction(environmental_data)
                
                # Extract statistics from results
                stats = results['statistics']
                mean_hsi = stats['mean_hsi']
                max_hsi = stats['max_hsi']
                min_hsi = stats['min_hsi']
                suitable_cells = stats['suitable_cells']
                
                # Display metrics
                st.success("✅ Analysis Complete!")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Mean HSI", f"{mean_hsi:.3f}")
                with col2:
                    st.metric("Max HSI", f"{max_hsi:.3f}")
                with col3:
                    st.metric("Min HSI", f"{min_hsi:.3f}")
                with col4:
                    st.metric("Suitable Cells", suitable_cells)
                
                # Create tabs for different visualizations
                tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗺️ Habitat Map", "📊 Distribution", "🥧 Quality Breakdown", "📋 Detailed Report", "🌊 Simple Summary"])
                
                with tab1:
                    st.plotly_chart(create_habitat_map(results, species_info), use_container_width=True)
                
                with tab2:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.plotly_chart(create_hsi_distribution(results), use_container_width=True)
                    with col2:
                        st.plotly_chart(create_quality_pie_chart(results), use_container_width=True)
                
                with tab3:
                    # Quality breakdown table
                    hsi_flat = np.array(results['hsi']).flatten()
                    total_points = len(hsi_flat)
                    
                    quality_data = {
                        'Quality Level': ['Excellent (>0.8)', 'Good (0.6-0.8)', 'Moderate (0.4-0.6)', 'Poor (0.2-0.4)', 'Unsuitable (≤0.2)'],
                        'Count': [
                            np.sum(hsi_flat > 0.8),
                            np.sum((hsi_flat > 0.6) & (hsi_flat <= 0.8)),
                            np.sum((hsi_flat > 0.4) & (hsi_flat <= 0.6)),
                            np.sum((hsi_flat > 0.2) & (hsi_flat <= 0.4)),
                            np.sum(hsi_flat <= 0.2)
                        ]
                    }
                    quality_data['Percentage'] = [f"{(count/total_points)*100:.1f}%" for count in quality_data['Count']]
                    
                    quality_df = pd.DataFrame(quality_data)
                    st.dataframe(quality_df, use_container_width=True)
                
                with tab4:
                    # Generate detailed report
                    st.subheader("📋 Detailed Analysis Report")

                    # Calculate detailed statistics
                    hsi_flat = np.array(results['hsi']).flatten()
                    stats = results['statistics']

                    # Generate comprehensive report
                    report = f"""
🦈 SHARK HABITAT ANALYSIS REPORT
================================================================================
Species: {species_info['name']} ({species_info['scientific']})
Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Study Area: {selected_location}

📊 HABITAT SUITABILITY STATISTICS:
   Mean HSI: {stats['mean_hsi']:.4f}
   Maximum HSI: {stats['max_hsi']:.4f}
   Minimum HSI: {stats['min_hsi']:.4f}
   Standard Deviation: {stats['std_hsi']:.4f}
   Total Analysis Cells: {stats['total_cells']}
   Suitable Habitat Cells: {stats['suitable_cells']}

🌊 HABITAT QUALITY DISTRIBUTION:
   Excellent (>0.8): {np.sum(hsi_flat > 0.8)} cells ({np.sum(hsi_flat > 0.8)/len(hsi_flat)*100:.1f}%)
   Good (0.6-0.8): {np.sum((hsi_flat > 0.6) & (hsi_flat <= 0.8))} cells ({np.sum((hsi_flat > 0.6) & (hsi_flat <= 0.8))/len(hsi_flat)*100:.1f}%)
   Moderate (0.4-0.6): {np.sum((hsi_flat > 0.4) & (hsi_flat <= 0.6))} cells ({np.sum((hsi_flat > 0.4) & (hsi_flat <= 0.6))/len(hsi_flat)*100:.1f}%)
   Poor (0.2-0.4): {np.sum((hsi_flat > 0.2) & (hsi_flat <= 0.4))} cells ({np.sum((hsi_flat > 0.2) & (hsi_flat <= 0.4))/len(hsi_flat)*100:.1f}%)
   Unsuitable (≤0.2): {np.sum(hsi_flat <= 0.2)} cells ({np.sum(hsi_flat <= 0.2)/len(hsi_flat)*100:.1f}%)

🔬 SPECIES CHARACTERISTICS:
   Optimal Temperature: {species_info['optimal_temp']}°C
   Temperature Range: {species_info['temp_range']}
   Depth Range: {species_info['depth_range']}
   Habitat Type: {species_info['habitat']}
   Hunting Strategy: {species_info['hunting']}
   Migration Pattern: {species_info['migration']}

🛰️ INPUT AND PROVENANCE BOUNDARY:
   - NASA CMR metadata lookup
   - Deterministic prototype environmental grids when direct processing is unavailable
   - Species preference parameters collected for educational exploration
   - No tagged-animal observations or field validation

🧮 MODEL COMPONENTS:
   - Bioenergetic Temperature Model (Sharpe-Schoolfield)
   - Trophic Transfer Model (Eppley + Lindeman)
   - Frontal Zone Detection (Multi-scale gradients)
   - Species-specific Depth Preferences
   - Ecological Factor Integration
   - Uncertainty Quantification

📈 SAFE INTERPRETATION:
   - Compare how the heuristic responds to different parameters
   - Treat score changes as software output, not animal-presence evidence
   - Do not use this map for conservation, navigation, or field decisions

🔬 EVIDENCE STATUS:
   Educational software prototype. Accuracy has not been measured against
   tagged sharks, field surveys, or a named ecological benchmark.

================================================================================
Generated by: Shark Habitat Suitability Explorer
Result type: deterministic heuristic prototype
"""

                    st.text_area("Detailed Analysis Report", report, height=400)

                    # Download button for report
                    st.download_button(
                        label="📥 Download Report",
                        data=report,
                        file_name=f"shark_habitat_report_{selected_species}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )

                with tab5:
                    # User-friendly simple summary
                    st.subheader("🌊 What Does This Mean? (Simple Explanation)")

                    # Get basic stats
                    hsi_flat = np.array(results['hsi']).flatten()
                    mean_hsi = np.mean(hsi_flat)
                    excellent_percent = (np.sum(hsi_flat > 0.8) / len(hsi_flat)) * 100
                    good_percent = (np.sum((hsi_flat > 0.6) & (hsi_flat <= 0.8)) / len(hsi_flat)) * 100

                    # Overall assessment
                    if mean_hsi > 0.7:
                        overall_rating = "🟢 **EXCELLENT**"
                        overall_message = f"This is a fantastic area for {species_info['name']}! The conditions are nearly perfect."
                    elif mean_hsi > 0.5:
                        overall_rating = "🟡 **GOOD**"
                        overall_message = f"This is a good area for {species_info['name']}. You'd likely find them here regularly."
                    elif mean_hsi > 0.3:
                        overall_rating = "🟠 **MODERATE**"
                        overall_message = f"This area is okay for {species_info['name']}. They might visit occasionally."
                    else:
                        overall_rating = "🔴 **POOR**"
                        overall_message = f"This area is not ideal for {species_info['name']}. They would rarely be found here."

                    # Display simple summary
                    st.markdown(f"""
                    ### 🎯 **Overall Habitat Rating: {overall_rating}**

                    {overall_message}

                    ---

                    ### 📊 **Quick Stats:**
                    - **🏆 Excellent Habitat**: {excellent_percent:.1f}% of the area
                    - **✅ Good Habitat**: {good_percent:.1f}% of the area
                    - **📍 Best Spots**: {np.sum(hsi_flat > 0.6)} locations found

                    ### 🦈 **What This Shark Likes:**
                    """)

                    # Species-specific preferences in simple language
                    species_key = selected_species
                    if species_key == 'great_white':
                        st.markdown("""
                        - 🌡️ **Cool water** (like California coast in fall)
                        - 🦭 **Areas with seals** (their favorite food!)
                        - 🌊 **Temperature boundaries** where different waters meet
                        - 🏔️ **Not too deep** - they hunt near the surface
                        """)
                    elif species_key == 'tiger_shark':
                        st.markdown("""
                        - 🌴 **Warm tropical water** (like Hawaii year-round)
                        - 🐢 **Everything is food** - they eat almost anything!
                        - 🏝️ **Near islands and reefs**
                        - 🌙 **More active at night**
                        """)
                    elif species_key == 'bull_shark':
                        st.markdown("""
                        - 🔥 **Very warm water** (like Florida in summer)
                        - 🏞️ **Shallow areas** - they love river mouths!
                        - 🌊 **Can handle fresh water** (unique among sharks)
                        - 🦐 **Lots of small fish and rays** to eat
                        """)
                    elif species_key == 'hammerhead':
                        st.markdown("""
                        - 🌺 **Tropical warm water** (like Bahamas in winter)
                        - 🗂️ **Sandy bottoms** where rays hide
                        - 🔨 **Uses unique head shape** to hunt rays
                        - 👥 **Often found in groups** (schooling behavior)
                        """)
                    elif species_key == 'mako':
                        st.markdown("""
                        - 🌊 **Open ocean** (far from shore)
                        - ⚡ **Fast-moving water** with currents
                        - 🐟 **Big fast fish** like tuna (they're speed hunters!)
                        - 🌡️ **Moderate temperatures** (not too hot or cold)
                        """)
                    elif species_key == 'blue_shark':
                        st.markdown("""
                        - ❄️ **Cool water** (like North Atlantic)
                        - 🌊 **Deep open ocean** (they travel huge distances)
                        - 🦑 **Squid and small fish** (not picky eaters)
                        - 🧭 **Follow ocean currents** like highways
                        """)
                    elif species_key == 'whale_shark':
                        st.markdown("""
                        - 🌴 **Warm tropical water** (like Maldives)
                        - 🦐 **Plankton and small fish** (gentle giant!)
                        - 🌊 **Surface waters** where plankton blooms
                        - 📏 **Largest fish in the ocean** (up to 40 feet!)
                        """)
                    elif species_key == 'basking_shark':
                        st.markdown("""
                        - ❄️ **Cool temperate water** (like Scotland)
                        - 🦐 **Zooplankton** (filter feeder like whales)
                        - 🌊 **Surface waters** following food blooms
                        - 🚗 **Second largest fish** (up to 26 feet!)
                        """)
                    elif species_key == 'thresher_shark':
                        st.markdown("""
                        - 🌊 **Temperate open ocean** (moderate temperatures)
                        - 🐟 **Schooling fish** like sardines and anchovies
                        - 🎯 **Uses long tail** to stun prey (unique hunting!)
                        - 🏊 **Deep diving** capability (up to 500m)
                        """)
                    elif species_key == 'nurse_shark':
                        st.markdown("""
                        - 🏝️ **Warm shallow reefs** (like Caribbean)
                        - 🦀 **Bottom creatures** like crabs and small fish
                        - 😴 **Very docile** (safe to swim near)
                        - 🏠 **Stays close to reefs** (not migratory)
                        """)
                    elif species_key == 'reef_shark':
                        st.markdown("""
                        - 🏝️ **Coral reefs** (tropical paradise waters)
                        - 🐠 **Reef fish and rays** (reef ecosystem predator)
                        - 🏠 **Territorial** around specific reefs
                        - 🤿 **Popular with divers** (beautiful to observe)
                        """)
                    elif species_key == 'lemon_shark':
                        st.markdown("""
                        - 🌴 **Warm mangrove areas** (like Bahamas)
                        - 🐟 **Bonefish and rays** (shallow water prey)
                        - 🌱 **Uses mangroves** as nurseries for babies
                        - 🟡 **Yellow coloration** (perfect camouflage)
                        """)
                    elif species_key == 'blacktip_shark':
                        st.markdown("""
                        - 🏖️ **Shallow coastal waters** (near beaches)
                        - 🐟 **Schooling fish** (sardines, herrings)
                        - 🦘 **Famous for jumping** out of the water
                        - ⚫ **Black-tipped fins** (easy to identify)
                        """)
                    elif species_key == 'sandbar_shark':
                        st.markdown("""
                        - 🏖️ **Continental shelf** (moderate depths)
                        - 🐟 **Bottom fish and rays** (seafloor hunters)
                        - 🗺️ **Long migrations** along coastlines
                        - 📏 **Large and robust** (up to 8 feet)
                        """)
                    elif species_key == 'spinner_shark':
                        st.markdown("""
                        - 🌴 **Warm coastal waters** (tropical/subtropical)
                        - 🐟 **Schooling fish** (sardines, herrings)
                        - 🌀 **Spinning attacks** (leaps and spins!)
                        - 🏊 **Fast swimmer** (high-energy hunter)
                        """)
                    elif species_key == 'dusky_shark':
                        st.markdown("""
                        - 🌊 **Temperate coastal waters** (wide range)
                        - 🐟 **Large fish** (bluefish, tuna)
                        - 🗺️ **Epic migrations** (thousands of miles)
                        - 📏 **Large size** (up to 12 feet)
                        """)
                    elif species_key == 'silky_shark':
                        st.markdown("""
                        - 🌴 **Tropical open ocean** (far from shore)
                        - 🐟 **Tuna and squid** (pelagic prey)
                        - ✨ **Silky smooth skin** (very distinctive)
                        - 🌊 **Deep diving** (follows prey vertically)
                        """)
                    elif species_key == 'porbeagle_shark':
                        st.markdown("""
                        - ❄️ **Cold northern waters** (like North Atlantic)
                        - 🐟 **Mackerel and herring** (cold water fish)
                        - 🔥 **Warm-blooded** (endothermic like tuna)
                        - ⚡ **Very fast swimmer** (built for speed)
                        """)
                    elif species_key == 'longfin_mako':
                        st.markdown("""
                        - 🌴 **Tropical open ocean** (warmer than shortfin mako)
                        - 🐟 **Large fish** like tuna and billfish
                        - 🔥 **Warm-blooded** (endothermic predator)
                        - 🌊 **Deep diving** (up to 220m)
                        """)
                    elif species_key == 'salmon_shark':
                        st.markdown("""
                        - 🧊 **Cold North Pacific** (Alaska to California)
                        - 🐟 **Salmon and herring** (follows salmon runs)
                        - 🔥 **Warm-blooded** (like great white)
                        - 🏃 **Fast swimmer** (built for pursuit)
                        """)
                    elif species_key == 'sand_tiger':
                        st.markdown("""
                        - 🏖️ **Temperate coastal waters** (near shore)
                        - 🐟 **Bottom fish and rays** (ambush hunter)
                        - 😮 **Gulps air** (for buoyancy control)
                        - 🦷 **Scary teeth** (but relatively docile)
                        """)
                    elif species_key == 'scalloped_hammerhead':
                        st.markdown("""
                        - 🌴 **Tropical coastal waters** (warm seas)
                        - 🐟 **Schooling fish and squid** (group hunter)
                        - 👥 **Forms large schools** (hundreds together!)
                        - 🔨 **Scalloped head** (distinctive shape)
                        """)
                    elif species_key == 'smooth_hammerhead':
                        st.markdown("""
                        - 🌊 **Temperate coastal waters** (cooler than scalloped)
                        - 🐟 **Sardines and anchovies** (schooling fish)
                        - 🔨 **Smooth head edge** (no scallops)
                        - 🏊 **Strong swimmer** (long migrations)
                        """)
                    elif species_key == 'bonnethead_shark':
                        st.markdown("""
                        - 🏖️ **Shallow warm waters** (like Florida)
                        - 🦀 **Crabs and shrimp** (bottom feeder)
                        - 🌱 **Eats seagrass** (only omnivorous shark!)
                        - 👒 **Bonnet-shaped head** (smallest hammerhead)
                        """)
                    else:
                        # Fallback for any missing species
                        st.markdown(f"""
                        - 🌡️ **Temperature**: {species_info.get('temp_range', 'Variable')}
                        - 🏔️ **Depth**: {species_info.get('depth_range', 'Variable')}
                        - 🍽️ **Hunting**: {species_info.get('hunting', 'Species-specific')}
                        - 🏠 **Habitat**: {species_info.get('habitat', 'Various environments')}
                        """)

                    st.markdown("""
                    ---

                    ### 🤔 **What is this prototype useful for?**

                    **🎓 If you're a student:**
                    - Inspect how a multi-factor heuristic is implemented
                    - Compare deterministic outputs across configurations
                    - Practice testing, visualization, and provenance labelling

                    **🚫 Do not use it for:**
                    - Predicting where sharks are present
                    - Planning ocean activities or safety decisions
                    - Scientific, conservation, or policy evidence
                    """)

                    # Fun facts section
                    st.markdown("### 🎉 **Fun Shark Facts:**")

                    if species_key == 'great_white':
                        st.info("🦈 Great Whites can detect a single drop of blood in 25 gallons of water!")
                    elif species_key == 'tiger_shark':
                        st.info("🐅 Tiger Sharks are called the 'wastebasket of the sea' because they eat almost anything!")
                    elif species_key == 'bull_shark':
                        st.info("🏞️ Bull Sharks can swim up rivers and have been found 2,500 miles up the Amazon!")
                    elif species_key == 'hammerhead':
                        st.info("🔨 Hammerhead's weird head shape gives them 360-degree vision!")
                    elif species_key == 'mako':
                        st.info("⚡ Mako Sharks can swim up to 45 mph - faster than most boats!")
                    elif species_key == 'blue_shark':
                        st.info("🌍 Blue Sharks migrate up to 5,500 miles - that's like swimming across the Atlantic!")
                    elif species_key == 'whale_shark':
                        st.info("🐋 Whale Sharks are the largest fish in the ocean but only eat tiny plankton!")
                    elif species_key == 'basking_shark':
                        st.info("🦈 Basking Sharks can filter 2,000 tons of water per hour through their gills!")
                    elif species_key == 'thresher_shark':
                        st.info("🎯 Thresher Sharks use their tail like a whip to stun entire schools of fish!")
                    elif species_key == 'nurse_shark':
                        st.info("😴 Nurse Sharks are so docile you can literally pet them (but don't try this at home)!")
                    elif species_key == 'reef_shark':
                        st.info("🏝️ Caribbean Reef Sharks are like the neighborhood watch of coral reefs!")
                    elif species_key == 'lemon_shark':
                        st.info("🍋 Lemon Sharks return to the exact same mangrove where they were born to have babies!")
                    elif species_key == 'blacktip_shark':
                        st.info("🦘 Blacktip Sharks can jump 6 feet out of the water while hunting!")
                    elif species_key == 'sandbar_shark':
                        st.info("🗺️ Sandbar Sharks migrate over 2,000 miles along the US East Coast every year!")
                    elif species_key == 'spinner_shark':
                        st.info("🌀 Spinner Sharks can spin up to 3 times in the air during their attacks!")
                    elif species_key == 'dusky_shark':
                        st.info("📏 Dusky Sharks can live over 40 years and don't have babies until they're 20!")
                    elif species_key == 'silky_shark':
                        st.info("✨ Silky Sharks have the smoothest skin of any shark - like touching silk!")
                    elif species_key == 'porbeagle_shark':
                        st.info("🔥 Porbeagle Sharks are warm-blooded and can heat their bodies 20°F above water temperature!")
                    elif species_key == 'longfin_mako':
                        st.info("🌊 Longfin Makos have the longest pectoral fins of any mako shark - perfect for deep ocean gliding!")
                    elif species_key == 'salmon_shark':
                        st.info("🐟 Salmon Sharks can eat up to 25% of their body weight in salmon during feeding season!")
                    elif species_key == 'sand_tiger':
                        st.info("😮 Sand Tiger Sharks gulp air at the surface to control their buoyancy - like a built-in life jacket!")
                    elif species_key == 'scalloped_hammerhead':
                        st.info("👥 Scalloped Hammerheads form the largest shark schools on Earth - sometimes over 500 sharks together!")
                    elif species_key == 'smooth_hammerhead':
                        st.info("🔨 Smooth Hammerheads can migrate over 4,000 miles - one of the longest shark migrations recorded!")
                    elif species_key == 'bonnethead_shark':
                        st.info("🌱 Bonnethead Sharks are the only omnivorous sharks - they actually digest seagrass for nutrients!")
                    else:
                        st.info("🦈 Sharks have been around for over 400 million years - they're older than trees!")
                
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                st.error(f"🔍 Error details: {type(e).__name__}")

                # Show debugging info
                with st.expander("🔧 Debug Information"):
                    st.write(f"Selected species: {selected_species}")
                    st.write(f"Species info: {species_info}")

                    # Try to show available species
                    try:
                        temp_framework = AutomaticNASAFramework()
                        available_species = temp_framework.get_available_species()
                        st.write(f"Available framework species: {available_species}")
                        st.write(f"Species exists in framework: {selected_species in available_species}")
                    except Exception as debug_e:
                        st.write(f"Debug error: {debug_e}")

                st.info("💡 Tips:")
                st.info("- Make sure all dependencies are installed")
                st.info("- Try a smaller study area")
                st.info("- Check your internet connection for NASA data access")
                st.info("- Try a different species")
    
    else:
        # Welcome screen
        st.markdown("""
        ## 🌊 Welcome to the Shark Habitat Suitability Explorer

        This learning prototype combines configurable species preferences with
        environmental demo grids to explore how a heuristic suitability score behaves.
        It is not a tracking system, validated ecological model, or research product.
        
        ### 🚀 What the prototype demonstrates:
        - **18 configurable shark profiles**
        - **Deterministic environmental demo layers**
        - **Species differentiation** based on preference parameters
        - **Interactive habitat maps** with zoom and pan
        - **Statistical summaries** of the generated score surface
        - **Downloadable reports** with an explicit evidence boundary
        - **User-friendly summaries** in plain language

        ### 📋 How to Use:
        1. **🦈 Select your shark species** from the dropdown (18 species available)
        2. **📍 Choose a study location** from preset options (California, Florida, Australia, etc.)
        3. **🔧 Optionally modify coordinates** for custom areas
        4. **📅 Set your time period** for analysis
        5. **🚀 Click "Run Analysis"** to generate habitat predictions

        ### 🌍 Popular Study Locations:
        - **🌊 California Coast**: Great White shark hotspot
        - **🏝️ Florida Keys**: Tiger & Bull shark habitat
        - **🦘 Great Barrier Reef**: Diverse shark species
        - **🇿🇦 South Africa**: Great White aggregation sites
        - **🌺 Hawaiian Islands**: Tiger shark territory
        - **🎯 Custom Location**: Set your own coordinates anywhere!
        
        ### 🔬 Scoring inputs:
        The heuristic includes:
        - Sea Surface Temperature (SST) preferences
        - Chlorophyll-a concentration (productivity)
        - Thermal frontal zones
        - Species-specific ecological parameters
        
        **Ready to inspect the prototype? Configure an analysis in the sidebar.**
        """)

if __name__ == "__main__":
    main()
