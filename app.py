import streamlit as st
import pandas as pd
import geopandas as gpd
import pydeck as pdk

# ===============================
# LOAD DATA
# ===============================
df = pd.read_csv("final_clean_tourism_risk_dataset.csv")
gdf = gpd.read_file("risk-map.geojson")

st.set_page_config(layout="wide")

st.title("🌍 Tourism Risk Analysis System (India)")

# ===============================
# SIDEBAR FILTERS
# ===============================
st.sidebar.header("Filters")

years = st.sidebar.multiselect(
    "Select Year",
    sorted(df['Year'].unique()),
    default=sorted(df['Year'].unique())
)

cities = st.sidebar.multiselect(
    "Select City",
    sorted(df['City'].unique())
)

risk_range = st.sidebar.slider(
    "Risk Range",
    float(df['Risk'].min()),
    float(df['Risk'].max()),
    (float(df['Risk'].min()), float(df['Risk'].max()))
)

# Apply filters
filtered = df[df['Year'].isin(years)]

if cities:
    filtered = filtered[filtered['City'].isin(cities)]

filtered = filtered[
    (filtered['Risk'] >= risk_range[0]) &
    (filtered['Risk'] <= risk_range[1])
]

# ===============================
# COLOR FUNCTION
# ===============================
def get_color(risk):
    if risk < 1.5:
        return [0, 200, 0]
    elif risk < 2:
        return [255, 255, 0]
    elif risk < 2.5:
        return [255, 140, 0]
    else:
        return [255, 0, 0]

filtered['color'] = filtered['Risk'].apply(get_color)

# ===============================
# MAP SECTION
# ===============================
st.subheader("📍 Risk Map (Points)")

layer = pdk.Layer(
    "ScatterplotLayer",
    data=filtered,
    get_position='[LON, LAT]',
    get_fill_color='color',
    get_radius=60000,
    pickable=True,
)

view = pdk.ViewState(latitude=22, longitude=78, zoom=4)

deck = pdk.Deck(layers=[layer], initial_view_state=view)

st.pydeck_chart(deck)

# ===============================
# GEOJSON MAP
# ===============================
st.subheader("🗺️ GeoJSON Layer (QGIS Export)")

geo_layer = pdk.Layer(
    "GeoJsonLayer",
    gdf,
    opacity=0.3,
    stroked=True,
    filled=True,
)

deck_geo = pdk.Deck(layers=[geo_layer], initial_view_state=view)

st.pydeck_chart(deck_geo)

# ===============================
# CHARTS
# ===============================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Avg Risk by City")
    city_risk = filtered.groupby('City')['Risk'].mean().sort_values(ascending=False)
    st.bar_chart(city_risk)

with col2:
    st.subheader("📈 Risk Trend")
    trend = filtered.groupby('Year')['Risk'].mean()
    st.line_chart(trend)

# ===============================
# TOP RISK CITIES
# ===============================
st.subheader("🚨 Top 10 Risk Cities")

top = filtered.sort_values(by='Risk', ascending=False).head(10)
st.table(top[['City','Year','Risk']])

# ===============================
# BEST TIME TO VISIT
# ===============================
st.subheader("✅ Best Time to Visit")

best = df.loc[df.groupby('City')['Risk'].idxmin()]
st.table(best[['City','Year','Risk']])

# ===============================
# DATA TABLE
# ===============================
st.subheader("📋 Full Dataset")

st.dataframe(filtered)