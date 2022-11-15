import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import streamlit_folium
from streamlit_folium import folium_static



df = pd.read_csv("hackathon/testdata2.csv", encoding="utf-8")


with st.sidebar:
  st.write("Test test test")
  st.info("Diese App entstand im ersten Hackathon der DNB.")


st.header("DNB-Hackathon: Exil-Monographien") 


#marker_cluster = MarkerCluster().add_to(m)

st.dataframe(df)

lat=df["lat"].values[0]
long=df["long"].values[0]

m = folium.Map(location=[lat, long], zoom_start=5)
#m = folium.Map(location=[df(lat), df(long)], zoom_start=5)
#m = folium.Map(df, x="long", y="lat", zoom_start=5)
#m = folium.Map(location=[39.949610, -75.150282], zoom_start=5)
marker_cluster = MarkerCluster().add_to(m)
folium_static(m)
