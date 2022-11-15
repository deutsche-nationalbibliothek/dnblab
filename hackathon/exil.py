import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import streamlit_folium



df = pd.read_csv("hackathon/testdata2.csv", encoding="utf-8")


with st.sidebar:
  st.write("Test test test")
  st.info("Diese App entstand im ersten Hackathon der DNB.")


st.header("DNB-Hackathon: Exil-Monographien") 

#m = folium.Map(df, x="long", y="lat", zoom_start=5)
#marker_cluster = MarkerCluster().add_to(m)

st.dataframe(df)

m = folium.Map(location=[39.949610, -75.150282], zoom_start=5)
marker_cluster = MarkerCluster().add_to(m)
folium_static(m)
#st.map(m)
