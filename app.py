import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ─────────────────────────────
# Page setup
st.set_page_config(
    page_title="Geopolitical Risk Dashboard",
    layout="wide"
)

st.title("🌍 Malta Geopolitical Risk Dashboard")
st.markdown("Real-time geopolitical events with AI-estimated impact on Malta")

# ─────────────────────────────
# Data source
DATA_URL = "https://drive.google.com/uc?export=download&id=1mU9wEJBrUMidZmeVkXtIPVYL6WCDQp9q"

@st.cache_data(ttl=300)
def load_data(url):
    df = pd.read_csv(url)
    return df

df = load_data(DATA_URL)

# ─────────────────────────────
# Basic cleanup
latest_update = df.get("latest_update", pd.Series(["N/A"])).iloc[0]

df = df.copy()

# Ensure numeric impact
if "level_of_impact" in df.columns:
    df["level_of_impact"] = pd.to_numeric(df["level_of_impact"], errors="coerce")

# Filter valid coordinates
df_map = df.dropna(subset=["latitude", "longitude"])
df_map = df_map[(df_map["latitude"] != 0) & (df_map["longitude"] != 0)]

# ─────────────────────────────
# Sidebar filters
st.sidebar.header("Filters")

event_types = sorted(df_map["event_type"].dropna().unique().tolist())
selected_types = st.sidebar.multiselect(
    "Event types",
    event_types,
    default=event_types
)

sources = sorted(df_map["source"].dropna().unique().tolist())
selected_sources = st.sidebar.multiselect(
    "Sources",
    sources,
    default=sources
)

# Apply filters
df_map_filtered = df_map[
    (df_map["event_type"].isin(selected_types)) &
    (df_map["source"].isin(selected_sources))
].copy()

# ─────────────────────────────
# Color mapping
color_map = {
    "conflict": "red",
    "military": "blue",
    "diplomacy": "green"
}

# ─────────────────────────────
# Layout (Map + Impact Panel)
col_map, col_impact = st.columns([3, 1])

# =========================================================
# LEFT: MAP
# =========================================================
with col_map:

    st.subheader("🗺️ Global Events Map")
    st.caption(f"Last update: {latest_update}")

    if not df_map_filtered.empty:

        center_lat = df_map_filtered["latitude"].mean()
        center_lon = df_map_filtered["longitude"].mean()

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=2,
            tiles="CartoDB positron"
        )

        for _, row in df_map_filtered.iterrows():

            color = color_map.get(row.get("event_type"), "gray")

            popup_html = f"""
            <b>{row.get('title','')}</b><br>
            <b>Source:</b> {row.get('source','')}<br>
            <b>Type:</b> {row.get('event_type','')}<br>
            <b>Location:</b> {row.get('location','')}<br>
            <b>Impact:</b> {row.get('level_of_impact','N/A')}<br>
            <a href="{row.get('link','#')}" target="_blank">Read Article</a>
            """

            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=7,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                popup=folium.Popup(popup_html, max_width=250)
            ).add_to(m)

        st_folium(m, width=900, height=600)

    else:
        st.info("No events match selected filters.")


# =========================================================
# RIGHT: IMPACT PANEL
# =========================================================
with col_impact:

    st.subheader("🚨 Malta Risk")

    if "level_of_impact" in df_map_filtered.columns:

        df_top = (
            df_map_filtered
            .dropna(subset=["level_of_impact"])
            .sort_values(by="level_of_impact", ascending=False)
            .head(5)
        )

        if not df_top.empty:

            # Top metric
            max_impact = int(df_top["level_of_impact"].max())
            st.metric("Highest Impact", max_impact)

            # Helper for color emoji
            def impact_icon(score):
                if score >= 8:
                    return "🔴"
                elif score >= 5:
                    return "🟠"
                else:
                    return "🟢"

            # Event cards
            for _, row in df_top.iterrows():

                score = int(row["level_of_impact"])

                with st.container():
                    st.markdown(
                        f"{impact_icon(score)} **{row['title'][:60]}...**"
                    )

                    st.progress(score / 10)

                    st.caption(
                        f"{row.get('location','')} • {row.get('event_type','')}"
                    )

                    if "description" in row:
                        st.caption(row["description"][:120])

                    st.markdown(f"[Read more]({row['link']})")

                    st.divider()

        else:
            st.info("No impact data available.")

    else:
        st.warning("Impact data missing.")

# ─────────────────────────────
# Footer summary
st.markdown("---")

if "level_of_impact" in df_map_filtered.columns:
    avg_impact = df_map_filtered["level_of_impact"].mean()

    st.markdown("### 📊 Quick Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Average Impact", round(avg_impact, 2))

    with col2:
        st.metric("Events Count", len(df_map_filtered))
