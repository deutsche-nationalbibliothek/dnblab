import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import streamlit_folium
from streamlit_folium import folium_static
import pydeck as pdk


#df = pd.read_csv("hackathon/alldata.csv", encoding="utf-8")
df = pd.read_csv("hackathon/exilarchiv_monografien-mit-geoloc_v2.csv", encoding="utf-8")
df = df.dropna(subset="lat")


with st.sidebar:
  st.write("Test test test")
  st.info("Diese App entstand im ersten Hackathon der DNB.")


st.header("DNB-Hackathon: Exil-Monographien") 
st.subheader("Erste Möglichkeit:")

lat=df["lat"].values[1]
long=df["long"].values[1]

year = st.slider('Wählen Sie eine Jahreszahl', 1933, 1950)
year = str(year)
st.write(year)

df_query = df.query("Erscheinungsjahr == @year")


#-- KARTE1 
m = folium.Map(location=[lat, long], zoom_start=2)

icon_create_function = """\
function(cluster) {
    return L.divIcon({
    html: '<b>' + cluster.getChildCount() + '</b>',
    className: 'marker-cluster marker-cluster-large',
    iconSize: new L.Point(20, 20)
    });
}"""

marker_cluster = MarkerCluster(
    name='1000 clustered icons',
    overlay=True,
    control=False,
    icon_create_function=icon_create_function
)

for i in range(0,len(df_query)):
    location = [df_query.iloc[i]['lat'], df_query.iloc[i]['long']]
    marker = folium.Marker(location=location)
    popup = 'Erscheinungsort:{}'.format(df_query.iloc[i]['Erscheinungsort'])
    folium.Popup(popup).add_to(marker)
    marker_cluster.add_child(marker)


#marker_cluster = MarkerCluster().add_to(m)
#for i in range(0,len(df_query)):
#   folium.Marker(
#      location=[df_query.iloc[i]['lat'], df_query.iloc[i]['long']],
#      popup=df_query.iloc[i]['Erscheinungsort'],
#   ).add_to(m)

folium_static(m)

st.write("Anzahl Datensätze: ", len(df_query))
st.dataframe(df_query)


# -- KARTE2
st.subheader("Zweite Möglichkeit") 

year2 = st.slider('Wählen Sie eine weitere Jahreszahl', 1933, 1950)
year2 = str(year2)

df_map = df.rename(columns={'long': 'lon'})
df_query2 = df_map.query("Erscheinungsjahr == @year2")
st.map(df_query2)



st.subheader("Dritte Möglichkeit")

df_test = df[['idn', 'lat', 'long']].copy()
st.dataframe(df_test)


layer = pdk.Layer(
    "ScatterplotLayer",
    df_test,
    pickable=True,
    opacity=0.8,
    stroked=True,
    filled=True,
    radius_scale=6,
    radius_min_pixels=10,
    radius_max_pixels=100,
    line_width_min_pixels=1,
    get_position='[long, lat]',
    #get_radius=50,
    get_fill_color=[255, 140, 0],
    get_line_color=[0, 0, 0],
)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=lat,
        longitude=long,
        zoom=3,
        pitch=50,
    ),
))
