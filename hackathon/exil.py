import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import pydeck as pdk

# load data:
df_all = pd.read_csv("hackathon/exilarchiv_data.csv", sep=';', encoding="utf-8")
# unique entries: 
unique = df_all.drop_duplicates("idn")
publications = len(unique)
# delete all rows that don't have an entry for lat:
df = df_all.dropna(subset="lat")   #This is mostly relevant for place entries "sine loco"
missing = len(df_all) - len(df)



# -- SIDEBAR --

with st.sidebar:
    st.markdown(" ##### Das Projekt")
    st.write("Ziel des DNB-Hackathon-Projektes war es, in zwei Tagen einen Prototyp einer leicht nutzbaren App zu "
             "entwickeln, die die Erscheinungsorte der Exilmonografien auf einer Weltkarte anzeigt und weitere "
             "Informationen den interessierten Nutzer*innen bietet, die sie für ihre Forschungen benötigen. Hierzu "
             "wurden die Metadaten der Exilmonografien (DNBLab - Datenset 07, ca. 20.000 Datensätze) "
             " genutzt werden. Unser Hackathon-Team besteht aus Dörte Asmussen, Kerstin Meinel, Stephanie Palek, "
             "Clemens Wahle, Maximilian Kähler und Jörn Hasenclever.")
    team = "https://raw.githubusercontent.com/deutsche-nationalbibliothek/dnblab/main/hackathon/Team.jpg"
    st.image(team)

    st.write(" ")
    st.write("Anzahl der im Datenset enthaltenen Einträge: ", publications)
    st.write("Anzahl Einträge ohne Ortsangabe: ", missing)
    st.markdown("Zuletzt aktualisiert: 13.07.2023")
    
# st.info("Diese App entstand im ersten Hackathon der DNB.")

# -- TEXT --

st.header("DNB-Hackathon: Exil-Monografien") 
col1, col2 = st.columns([3, 1])
col1.write("""
        Das Deutsche Exilarchiv 1933–1945 bewahrt in seiner Sammlung knapp 30.000 Exilpublikationen. Darunter von 
        Emigrantinnen und Emigranten verfasste Werke in Erstausgaben, Nachauflagen und Übersetzungen sowie Sammelbände, 
        an denen Emigrantinnen und Emigranten mitgearbeitet haben, darüber hinaus von Emigrantinnen und Emigranten 
        herausgegebene, übersetzte, illustrierte und gestaltete Bücher. Hinzu kommt die Produktion von Exilverlagen. 
        Auch Veröffentlichungen aus Deutschland, Österreich und der Tschechoslowakei nach 1933, die im Zusammenhang 
        mit Emigration stehen, gehören zum Sammelgebiet. Forschende befragen das DEA immer wieder zu Themen wie:  
        Wo sind Exilmonografien entstanden? Wie verteilen sich Exilmonografien auf die Erscheinungsländer und 
        Erscheinungsorte? Wo sind die meisten Exilmonografien entstanden? Was sind die entlegensten Erscheinungsorte?
         """)
col2.image("https://raw.githubusercontent.com/deutsche-nationalbibliothek/dnblab/main/hackathon/"
           "image2022-11-16_9-7-49.png")

# set default long/lat value for map focus:
lat = df["lat"].values[5]
long = df["long"].values[5]


# - MAPS --

# -- MAP1: Darstellung aller Exil-Monografien im Set nach Häufigkeit der Verlagsorte --

st.markdown("#### Darstellung aller Exil-Monografien im Set nach Häufigkeit der Verlagsorte") 

# create subset of data only including idn, pubplace, lat and long: 
df_map1 = df[['idn', 'pubplace', 'lat', 'long']].copy()  # extract neccessary columns from df
#df_map1["pubplace"] = df_map1["pubplace"].str.strip("[]")

# create new dataframe by grouping by "placename" and adding count of unique entries, 
# then merge on "pubplace" to map lat and long to "placename" and create new dataframe without duplicates:
df_map2 = df_map1.groupby(["pubplace"]).size().reset_index(name='counts')
dfmerge = pd.merge(df_map1, df_map2, on=['pubplace'], how="left")
places = dfmerge.drop_duplicates(['pubplace'], keep='first')

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
        longitude=long,
        latitude=lat,
        zoom=2,
        pitch=50,
    ),
    tooltip={"text": "{pubplace}\n{counts}"}
))

st.write("Anzahl unterschiedlicher Ortsangaben im Datenset: ", len(df_map2))

st.markdown("Zu den [Exil-Monografien im Katalog der Deutschen Nationalbibliothek]"
            "(https://portal.dnb.de/opac.htm?query=catalog%3Ddnb.dea.exilpub&method=simpleSearch&cqlMode=true)")
st.write(" ")


# --- Map2 ---

st.markdown("#### Darstellung der Verlagsorte nach Erscheinungsjahren")

year = st.slider('Wählen Sie eine Jahreszahl', 1933, 1950)
df_query = df.query("Erscheinungsjahr == @year")
       
m = folium.Map(location=[lat, long], zoom_start=2)

for i in range(0, len(df_query)):
    url1 = "https://d-nb.info/" + df_query.iloc[i]['idn']
    link1 = f"<a href='{url1}', target='new'>" + df_query.iloc[i]['idn'] + "</a>"
    popup = df_query.iloc[i]['pubplace']+", IDN: "+link1,
    folium.Marker(
        location=[df_query.iloc[i]['lat'], df_query.iloc[i]['long']],
        popup=popup,
    ).add_to(m)
    
marker_cluster = MarkerCluster().add_to(m)
    
folium_static(m)

st.write(f"Anzahl ausgewählter Datensätze der Exil-Monografien ({str(year)}): ", len(df_query))


# -- Map3 ---

st.markdown("#### Darstellung nach Sprachen der Exil-Monografien")
df_short = df[['idn', 'pubplace', 'sprache.text', 'lat', 'long']].copy()
df_short = df_short.rename(columns={'sprache.text': 'sprache'})
df_lang = df_short.dropna(subset="sprache")

lang = st.selectbox('Wählen Sie eine Sprache:', ('cze', 'eng', 'fre', 'ger', 'spa', 'tur', 'ita', 'spr'))
lang = str(lang)

df_lang = df_lang.query("sprache == @lang")
       
m = folium.Map(location=[lat, long], zoom_start=2)
marker_cluster = MarkerCluster().add_to(m)

for i in range(0, len(df_lang)):
    url2 = "https://d-nb.info/" + df_lang.iloc[i]['idn']
    link2 = f"<a href='{url2}', target='new'>" + df_lang.iloc[i]['idn'] + "</a>"
    newpopup = df_lang.iloc[i]['pubplace']+", IDN: "+link2,
    folium.Marker(
        location=[df_lang.iloc[i]['lat'], df_lang.iloc[i]['long']],
        popup=newpopup,
        ).add_to(marker_cluster)
       
folium_static(m)

st.write("Anzahl ausgewählter Datensätze der Exil-Monografien: ", len(df_lang))


# --- FOOTER ---

st.write(" ")
st.write(" ")
st.markdown(" ##### Lust bekommen, mit den Daten eigene Visualisierungen auszuprobieren? ")
st.markdown("Hier befindet sich unser Datenset zum Download: [DNBLab: Zugang zu Datensets und digitalen Objekte -"
            " Freie digitale Objektsammlungen](https://www.dnb.de/dnblabsets) ")
st.write(" ")

with st.expander("Methodik"):
    st.write(f""" 
          Im Datenset sind Einträge zu {publications} verschiedenen Publikationen enthalten. Bei der Datenaufbereitung für diese App
          wurden für solche Publikationen, denen mehrere Sprachen, Publikationsorte oder Verlage zugrunde liegen für 
          jede Sprache, jeden Publikationsort etc. ein eigener Eintrag zugeweisen, so dass diese Publikationen mehrfach in der
          hier zugrunde liegenden Excel-Tabelle enthalten sind. Insgesamt sind daher 27.953 Einträge zu verzeichnen. 
          
          Nicht alle Publikationen verfügen über die Angabe eines Erscheinungs- oder Verlagsortes. Im Datensatz steht 
          in solchen Fällen "s.l." bzw. eine Variante davon für "sine loco", also ohne Ortsangabe. Einträge
          mit diesem Vermerk können auf den Karten entsprechend nicht dargestellt werden. Diese Einträge werden
          in der Sidebar (links) anhand der "Anzahl Einträge ohne Ortsangabe" ausgewiesen.
             """)
