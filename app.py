import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ─────────────────────────────
# Page setup
st.set_page_config(
    page_title="Geopolitical Events Map",
    layout="wide"
)

st.title("🌍 Latest Geopolitical RSS Updates Map + Malta Impact Assessmnt")
st.markdown("Groq AI 🧠 used for geo location extraction 📍 and activity categorisation ⚔️ (Agent 1 🤖) and Malta ✠ Impact Assessment (Agent 2 👾).")

# ─────────────────────────────
DATA_URL = "https://drive.google.com/uc?export=download&id=1mU9wEJBrUMidZmeVkXtIPVYL6WCDQp9q"

@st.cache_data(ttl=300)  # cache for 5 minutes
def load_data(url):
    df = pd.read_csv(url)
    return df

df = load_data(DATA_URL)

latest_update = df["latest_update"].iloc[0]

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
].copy()

# Color mapping by event type
color_map = {
    'conflict': 'red',
    'military': 'blue',
    'diplomacy': 'green',
}

# ─────────────────────────────
# Create Folium map
st.subheader("Map View")
st.write(f"Latest update: {latest_update}")

if not df_map_filtered.empty:
    # Center on Middle East
    center_lat = 25
    center_lon = 45
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=3, tiles="CartoDB positron")
    
    # Add Malta marker
    folium.Marker(
        location=[35.9375, 14.3754],
        popup="🇲🇹 Malta",
        icon=folium.Icon(color="green")
    ).add_to(m)

    # Add markers
    for _, row in df_map_filtered.iterrows():
        color = color_map.get(row['event_type'], 'gray')
        popup_html = f"""
        <b>{row['title']}</b><br>
        Source: {row['source']}<br>
        Type: {row['event_type']}<br>
        Location: {row['location']}<br>
        Timestamp: {row['timestamp']}<br>
        Malta impact: {row['description']}<br>
        Level of impact: {row['level_of_impact']}<br>
        <a href="{row['link']}" target="_blank">Read Article</a>
        """
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=7,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(m)

    # Display Folium map in Streamlit
    st_data = st_folium(m, width=1200, height=600)
else:
    st.write("No events match the selected filters.")

# Top Impact Events
if "level_of_impact" in df_map_filtered.columns:

    # Ensure numeric
    df_map_filtered["level_of_impact"] = pd.to_numeric(
        df_map_filtered["level_of_impact"], errors="coerce"
    )

    df_top = (
        df_map_filtered
        .dropna(subset=["level_of_impact"])
        .query("level_of_impact >= 7")
        .sort_values(by="level_of_impact", ascending=False)
        .head(5)
    )

    if not df_top.empty:

        st.subheader("🚨 Top Impact on Malta")

        for _, row in df_top.iterrows():

            st.markdown(f"### {row['title']}")

            st.progress(min(int(row["level_of_impact"]), 10) / 10)

            st.markdown(f"""
            **Impact Level:** {row['level_of_impact']} / 10  
            **Type:** {row['event_type']}  
            **Location:** {row['location']}  
            **Source:** {row['source']}  
            **Reason of impact:** {row['description']}  

            [Read full article]({row['link']})
            ---
            """)

    else:
        st.info("No high-impact events (≥7) right now.")

else:
    st.warning("No impact data available.")
