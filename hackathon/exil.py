import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import streamlit_folium
from streamlit_folium import folium_static
import pydeck as pdk


df = pd.read_csv("hackathon/exilarchiv_monografien-mit-geoloc_v6_corr.csv", sep=';', encoding="utf-8")
#coord = pd.read_csv("hackathon/exilarchiv_monografien-mit-geoloc_v5.csv", encoding="utf-8")
df1 = pd.read_csv("hackathon/exilarchiv_monografien-mit-geoloc_v4.csv", encoding="utf-8")
df2 = pd.read_csv("hackathon/exilarchiv_monografien-mit-geoloc_v2.csv", encoding="utf-8")
df2 = df2.dropna(subset="lat")
df1 = df1.rename(columns={'sprache.text': 'sprache'})
df1 = df1.dropna(subset="lat")


## -- SIDEBAR -- 

with st.sidebar:
    st.markdown(" ##### Das Projekt")
    st.write("Ziel des DNB-Hackathon-Projektes war es, in zwei Tagen einen Prototyp einer leicht nutzbaren App zu entwickeln, die die "
             " Erscheinungsorte der Exilmonografien auf einer Weltkarte anzeigt und weitere Informationen den interessierten Nutzer*innen bietet, "
             " die sie für ihre Forschungen benötigen. Hierzu wurden die Metadaten der Exilmonografien (DNBLab - Datenset 07, ca. 30.000 Datensätze) "
             " genutzt werden. Unser Hackathon-Team besteht aus Dörte Asmussen, Kerstin Meinel, Stephanie Palek, Clemens Wahle, Maximilian Kähler und " 
             " Jörn Hasenclever.")
    team = "https://raw.githubusercontent.com/deutsche-nationalbibliothek/dnblab/main/hackathon/Team.jpg"
    st.image(team)
    
  #st.info("Diese App entstand im ersten Hackathon der DNB.")

## -- TEXT --

st.header("DNB-Hackathon: Exil-Monografien") 
col1, col2 = st.columns([3, 1])
col1.write("""
        Das Deutsche Exilarchiv 1933–1945 bewahrt in seiner Sammlung knapp 30.000 Exilpublikationen. Darunter von Emigrantinnen und Emigranten 
        verfasste Werke in Erstausgaben, Nachauflagen und Übersetzungen sowie Sammelbände, an denen Emigrantinnen und Emigranten mitgearbeitet haben, 
        darüber hinaus von Emigrantinnen und Emigranten herausgegebene, übersetzte, illustrierte und gestaltete Bücher. Hinzu kommt die Produktion 
        von Exilverlagen. Auch Veröffentlichungen aus Deutschland, Österreich und der Tschechoslowakei nach 1933, die im Zusammenhang mit Emigration 
        stehen, gehören zum Sammelgebiet. Forschende befragen das DEA immer wieder zu Themen wie:  Wo sind Exilmonografien entstanden? Wie verteilen 
        sich Exilmonografien auf die Erscheinungsländer und Erscheinungsorte? Wo sind die meisten Exilmonografien entstanden? Was sind die 
        entlegensten Erscheinungsorte?
         """)
col2.image("https://raw.githubusercontent.com/deutsche-nationalbibliothek/dnblab/main/hackathon/image2022-11-16_9-7-49.png")
    
lat=df1["lat"].values[1]
long=df1["long"].values[1]


## - MAPS -- 

# -- MAP1: Darstellung aller Exil-Monografien im Set nach Häufigkeit der Verlagsorte --

st.markdown("#### Darstellung aller Exil-Monografien im Set nach Häufigkeit der Verlagsorte") 

df_map1 = df[['idn', 'Erscheinungsort']].copy()  # extract neccessary columns from df
#df_coord = coord[['idn', 'Erscheinungsort', 'lat', 'Long']].copy()
#df_merge_map1 = pd.merge(df_map1, df_coord, on=['Erscheinungsort'], how="left")
#st.dataframe(df_merge_map1)
df_map1 = df_map1.rename(columns={'Erscheinungsort': 'place'})  # rename column
df_map1["place"] = df_map1["place"].str.strip("[]")    # remove square brackets from place names where present
df_map1_1 = df_map1.drop_duplicates() # remove duplicate entries

df_map1_2 = df_map1_1.groupby(["place"]).size().reset_index(name='counts')
st.dataframe(df_map1_2)
dfmerge = pd.merge(df_map1_1, df_map1_2, on=['place'], how="left")
places = dfmerge.drop_duplicates(['place'], keep='first')
st.dataframe(places)

#df_query2 = df_map
#st.map(places)
layer = pdk.Layer(
    "ScatterplotLayer",
    places,
    pickable=True,
    opacity=0.8,
    stroked=True,
    filled=True,
    radius_scale=6,
    radius_min_pixels=3,
    radius_max_pixels=50,
    line_width_min_pixels=1,
    get_position='[long, lat]',
    get_radius="counts",
    get_fill_color=[230, 45, 45],
    get_line_color=[0, 0, 0],
)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=lat,
        longitude=long,
        zoom=2,
        pitch=50,
    ),
    tooltip={"text": "{place}\n{counts}"}
))

st.write("Anzahl Datensätze der Exil-Monografien: ", len(df2))

st.markdown("Zu den [Exil-Monografien im Katalog der Deutschen Nationalbibliothek](https://portal.dnb.de/opac.htm?query=catalog%3Ddnb.dea.exilpub&method=simpleSearch&cqlMode=true)")




st.write(" ") 

# KARTE 1
st.markdown("#### Darstellung der Verlagsorte nach Erscheinungsjahren")

year = st.slider('Wählen Sie eine Jahreszahl', 1933, 1950)
year = str(year)


df_query = df2.query("Erscheinungsjahr == @year")
       
m = folium.Map(location=[lat, long], zoom_start=2)

for i in range(0,len(df_query)):
   popup=df_query.iloc[i]['Erscheinungsort']+", IDN: "+df_query.iloc[i]['idn'],
   folium.Marker(
      location=[df_query.iloc[i]['lat'], df_query.iloc[i]['long']],
      popup=popup,
   ).add_to(m)
    
marker_cluster = MarkerCluster().add_to(m)
    
folium_static(m)

st.write("Anzahl ausgewählter Datensätze der Exil-Monografien: ", len(df_query))



# KARTE 3
st.markdown("#### Darstellung nach Sprachen der Exil-Monografien")
df_short = df1[['idn', 'Erscheinungsort', 'sprache', 'lat', 'long']].copy()

lang = st.selectbox('Wählen Sie eine Sprache:', ('cze', 'eng', 'fre', 'ger', 'spa', 'tur', 'ita', 'spr'))
lang = str(lang)
    

df_lang = df_short.dropna(subset="sprache")
df_lang = df_lang.query("sprache == @lang")
       
m = folium.Map(location=[lat, long], zoom_start=2)
marker_cluster = MarkerCluster().add_to(m)

for i in range(0,len(df_lang)):
    newpopup=df_lang.iloc[i]['Erscheinungsort']+", IDN: "+df_lang.iloc[i]['idn'],
    folium.Marker(
        location=[df_lang.iloc[i]['lat'], df_lang.iloc[i]['long']],
        popup=newpopup,
        ).add_to(marker_cluster)
       
folium_static(m)

st.write("Anzahl ausgewählter Datensätze der Exil-Monografien: ", len(df_lang))

st.write(" ")
st.write(" ")
st.markdown(" ##### Lust bekommen mit den Daten eigene Visualisierungen auszuprobieren? ")
st.markdown("Hier befindet sich das Set: [DNB - DNBLab: Zugang zu Datensets und digitalen Objekten - DnbLab: Freie digitale Objektsammlungen](https://www.dnb.de/dnblabsets) ")







