import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import streamlit_folium
from streamlit_folium import folium_static


df = pd.read_csv("hackathon/alldata.csv", encoding="utf-8")

with st.sidebar:
  st.write("Test test test")
  st.info("Diese App entstand im ersten Hackathon der DNB.")


st.header("DNB-Hackathon: Exil-Monographien") 
st.subheader("Erste Möglichkeit:")


lat=df["lat"].values[1]
long=df["long"].values[1]

m = folium.Map(location=[lat, long], zoom_start=2)
#m = folium.Map(df, zoom_start=2)

marker_cluster = MarkerCluster().add_to(m)
for i in range(0,1000):
   folium.Marker(
      location=[df.iloc[i]['lat'], df.iloc[i]['long']],
      popup=df.iloc[i]['Erscheinungsort'],
   ).add_to(m)

folium_static(m)


st.subheader("Zweite Möglichkeit") 

df_map = df.rename(columns={'long': 'lon'})
st.map(df_map)


st.subheader("Dritte Möglichkeit") 

st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=lat,
        longitude=long,
        zoom=3,
        pitch=50,
    ),
        pdk.Layer(
            'ScatterplotLayer',
            data=df_map,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=200,
        ),
    ],
))
