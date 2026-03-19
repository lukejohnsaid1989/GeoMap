import streamlit as st
import pandas as pd
import pydeck as pdk

# ─────────────────────────────
# Page setup
st.set_page_config(
    page_title="Geopolitical Events Map",
    layout="wide"
)

st.title("🌍 Geopolitical Events Map")
st.markdown("This app loads your dataset from the Google Sheets CSV and visualizes events geographically.")

# ─────────────────────────────
# Load data from Google Sheets CSV
DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT8RR2iblV2jx-tt5lUTVzrGM5Kcb_JX-yknDp2KnfUhhe_Aep_kUN1GsSva6GtnLE2vslsXnxp0o5V/pub?output=csv"

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    return df

df = load_data(DATA_URL)

# Show raw dataset
st.subheader("Raw Data")
st.dataframe(df)

# ─────────────────────────────
# Clean and filter for valid coordinates
df_map = df.dropna(subset=["latitude", "longitude"])
df_map = df_map[(df_map["latitude"] != 0) & (df_map["longitude"] != 0)]

# ─────────────────────────────
# Map visualization
st.subheader("Map View")

if not df_map.empty:
    deck = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v10",
        initial_view_state=pdk.ViewState(
            latitude=df_map["latitude"].mean(),
            longitude=df_map["longitude"].mean(),
            zoom=2,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=df_map,
                get_position=["longitude", "latitude"],
                get_color="[255, 0, 0, 140]",
                get_radius=50000,
                pickable=True,
            )
        ],
        tooltip={
            "text": "{title}\nSource: {source}\nType: {event_type}\nLocation: {location}"
        },
    )

    st.pydeck_chart(deck)
else:
    st.write("No valid geographic data found.")

# ─────────────────────────────
# Detailed table of plotted events
st.subheader("Event Details")
st.dataframe(df_map)
