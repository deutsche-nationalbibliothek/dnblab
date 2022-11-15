import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import streamlit_folium
from streamlit_folium import folium_static
import pydeck as pdk


df = pd.read_csv("hackathon/alldata.csv", encoding="utf-8")
st.dataframe(df)

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

