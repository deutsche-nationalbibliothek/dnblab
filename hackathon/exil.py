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

marker_cluster = MarkerCluster().add_to(m)
for i in range(0,len(df_query)):
   folium.Marker(
      location=[df_query.iloc[i]['lat'], df_query.iloc[i]['long']],
      popup=df_query.iloc[i]['Erscheinungsort'],
   ).add_to(m)

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

st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=lat,
        longitude=long,
        zoom=3,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
           'HexagonLayer',
           data=df_test,
           get_position='[long, lat]',
           radius=200,
           elevation_scale=4,
           elevation_range=[0, 1000],
           pickable=True,
           extruded=True,
        ),  
        pdk.Layer(
            'ScatterplotLayer',
            data=df_test,
            get_position='[long, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=200,
        ),
      ],
    ))

