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

#marker_cluster = MarkerCluster().add_to(m)

st.dataframe(df)

lat=df["lat"].values[1]
long=df["long"].values[1]
st.write("lat: ",lat)
st.write("long: ", long)

m = folium.Map(location=[lat, long], zoom_start=5)

marker_cluster = MarkerCluster().add_to(m)

folium.Marker(
    location=[lat, long],
    popup="Add popup text here.",
    icon=folium.Icon(color="green", icon="ok-sign"),
).add_to(marker_cluster)

folium_static(m)


st.subheader("Zweie Möglichkeit") 
df_map = df.rename(columns={'long': 'lon'})

st.map(df_map)
