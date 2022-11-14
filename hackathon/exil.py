import streamlit as st
import pandas as pd

df = pd.read_csv("testdata1.csv", encoding="utf-8")


with st.sidebar:
  st.write("Test test test")
  st.info("Diese App entstand im ersten Hackathon der DNB.")


st.header("DNB-Hackathon: Exil-Monographien") 

st.table(df)
