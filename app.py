import streamlit as st
import pandas as pd
import pydeck as pdk

# ─────────────────────────────
# Page setup
st.set_page_config(
    page_title="Geopolitical Events Map",
    layout="wide"
)

st.title("🌍 Latest RSS Updates Map")
st.markdown("Groq AI used for geo location extraction and activity categorisation")

# ─────────────────────────────
# Load dataset
DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8RR2iblV2jx-tt5lUTVzrGM5Kcb_JX-yknDp2KnfUhhe_Aep_kUN1GsSva6GtnLE2vslsXnxp0o5V/pub?output=csv"

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    return df

df = load_data(DATA_URL)

# ─────────────────────────────
# Clean and filter valid coordinates
df_map = df.dropna(subset=["latitude", "longitude"])
df_map = df_map[(df_map["latitude"] != 0) & (df_map["longitude"] != 0)]

# ─────────────────────────────
# Sidebar filters
st.sidebar.header("Filters")

event_types = df_map['event_type'].dropna().unique().tolist()
selected_types = st.sidebar.multiselect("Select event types:", event_types, default=event_types)

sources = df_map['source'].dropna().unique().tolist()
selected_sources = st.sidebar.multiselect("Select sources:", sources, default=sources)

# Apply filters
df_map_filtered = df_map[
    (df_map['event_type'].isin(selected_types)) &
    (df_map['source'].isin(selected_sources))
].copy()  # avoid SettingWithCopyWarning

# Color mapping by event type
color_map = {
    'conflict': [255, 0, 0, 160],    # Red
    'military': [0, 0, 255, 160],    # Blue
    'diplomacy': [0, 255, 0, 160],   # Green
}

df_map_filtered['color'] = df_map_filtered['event_type'].map(lambda x: color_map.get(x, [200, 200, 200, 160]))

# ─────────────────────────────
# Map visualization
st.subheader("Map View")
if not df_map_filtered.empty:
    deck = pdk.Deck(
        map_style="road",  # default map style works without Mapbox token
        initial_view_state=pdk.ViewState(
            latitude=df_map_filtered["latitude"].mean(),
            longitude=df_map_filtered["longitude"].mean(),
            zoom=2,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=df_map_filtered,
                get_position=["longitude", "latitude"],
                get_fill_color="color",
                get_radius=50000,
                pickable=True,
            )
        ],
        tooltip={
            "html": "<b>{title}</b><br>Source: {source}<br>Type: {event_type}<br>Location: {location}",
            "style": {"color": "white"}
        },
    )
    st.pydeck_chart(deck)
else:
    st.write("No events match the selected filters.")

# ─────────────────────────────

