## DNB_Testabfrage für streamlit:

## Bibliotheken:
import streamlit as st
import requests
from IPython.display import display, clear_output
from bs4 import BeautifulSoup
from lxml import etree
import pandas
import unicodedata
from IPython.core.display import display, HTML

if 'letsgo' not in st.session_state:
    st.session_state.letsgo = 0
    
if 'downclick' not in st.session_state:
    st.session_state.downclick = 0


st.markdown("# Testabfrage DNB-Daten <img src='https://files.dnb.de/DFG-Viewer/DNB-Logo-Viewer.jpg' align='right'>", unsafe_allow_html=True)

st.markdown("Hier können Sie die SRU-Schnittstelle der Deutschen Nationalbibliothek über einfache Formulareingaben "
        "abfragen. Wählen Sie dazu den Katalog, den Sie abfragen möchten und das Metadatenformat für die Ausgabe "
        "aus. Im nächsten Schritt geben Sie Ihren Suchbegriff ein. Für die Ausführung des dahinterliegenden Codes "
        "muss die Reihenfolge bei Eingaben und Buttonklicks eingehalten werden. Im Anschluss können Sie sich eine "
        "gekürzte tabellarische Darstellung Ihrer Anfrage ansehen und diese als XML- oder CSV-Datei speichern. ")
        
st.markdown("**Bitte beachten Sie**:  \n"
            "* Dieses Tutorial dient als Einstieg. Aus Performance-Gründen werden jeweils "
            "immer nur die **ersten 100 Treffer** Ihrer Anfrage ausgegeben. \n"
            "* Die Metadatenformate enthalten "
            "unterschiedliche Informationen. Die Ausgabetabellen und -dateien variieren daher entsprechend in der "
            "Anzahl enthaltener Elemente und Informationen.")


st.markdown("##### Bitte wählen Sie zunächst den gewünschten Katalog:")
st.markdown("* DNB = Titeldaten der Deutschen Nationalbibliothek \n "
"* DMA = Deutsches Musikarchiv \n "
        "* GND = Gemeinsame Normdatei ")

##Erstes Dropdown:
auswahl = st.selectbox(
            'Katalog:', 
            ('DNB', 'DMA', 'GND'))
            
default = "https://services.dnb.de/sru/dnb"

#Zweites Dropdown:
st.markdown("##### Bitte wählen Sie das Metadatenformat für die Ausgabe:")

meta = st.selectbox(
        'Metadatenformat:',
        ('MARC21-xml', 'DNB Casual (oai_dc)', 'RDF (RDFxml)'))


if meta == "DNB Casual (oai_dc)":
    dataform = "oai_dc"
elif meta == "RDF (RDFxml)":
    dataform = "RDFxml"
elif meta == "MARC21-xml":
    dataform = "MARC21-xml"
else: 
    dataform = ""


#Übernahme der Parameter bei Click auf Bestätigen: 
if auswahl == "DNB":
        selected_url = "https://services.dnb.de/sru/dnb"
elif auswahl == "DMA":
        selected_url = "https://services.dnb.de/sru/dnb.dma"
elif auswahl == "GND":
        selected_url = "https://services.dnb.de/sru/authorities"
else:
        selected_url = "ERROR: Keine URL gewählt"  
#st.write('Katalog:', auswahl, ':', selected_url)
#st.write('Metadatenformat:', meta)


#Eingabe Suchbegriff: 
st.markdown("##### Bitte geben Sie nun Ihren Suchbegriff ein:")
searchterm = st.text_input('Suchbegriff:', placeholder="Bitte Suchbegriff eingeben")

confirm = st.button('Los!', key='push')
if confirm:
    st.session_state.letsgo += 1 
    
#Suche ausführen: 
def enquiry(): 
    parameter = {'version' : '1.1' , 'operation' : 'searchRetrieve' , 'query' : searchterm, 'recordSchema' : dataform, 
                'maximumRecords': '100'} 
    r1 = requests.get(selected_url, params = parameter)  
    return r1    


if confirm and searchterm:
    r1 = enquiry()
    response = BeautifulSoup(r1.content)
    
    records = response.find_all('record')
    records_marc = response.find_all('record', {'type':'Bibliographic'})
    gndm = response.find_all('record', {'type':'Authority'})
    results = response.find('numberofrecords')  
     
    numberofrecords = results.text
    numberofrecords = int(numberofrecords)
    st.write("Gefundene Treffer:", numberofrecords)
        
    if numberofrecords >= 1:
        st.markdown("##### Anzeige des ersten Treffers der SRU_Antwort:")    
        vorschau = records[0]
        with st.expander("Vorschau anzeigen"):
            st.code(vorschau)
    else: 
        st.write("Keine Treffer vorhanden")

elif confirm and not searchterm: 
    st.error("Sie haben keinen Suchbegriff eingegeben.")
else:
    st.write(' ')


## TEIL 2 -------------------------------------------------------------------------------------------


#Funktion für Titeldaten in OAI-DC
def parse_record_dc(record):
    
    ns = {"dc": "http://purl.org/dc/elements/1.1/", 
          "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
    xml = etree.fromstring(unicodedata.normalize("NFC", str(record)))
    
    #idn
    idn = xml.xpath(".//dc:identifier[@xsi:type='dnb:IDN']", namespaces=ns) #--> Adressiert das Element direkt   
    try:
        idn = idn[0].text
    except:
        idn = 'fail'
    
    #creator:
    creator = xml.xpath('.//dc:creator', namespaces=ns)
    try:
        creator = creator[0].text
    except:
        creator = "N/A"
    
    #titel
    titel = xml.xpath('.//dc:title', namespaces=ns)
    try:
        titel = titel[0].text
    except:
        titel = "N/A"
        
    #date
    date = xml.xpath('.//dc:date', namespaces=ns)
    try:
        date = date[0].text
    except:
        date = "N/A"
    
    #publisher
    publ = xml.xpath('.//dc:publisher', namespaces=ns)
    try:
        publ = publ[0].text
    except:
        publ = "N/A"
     
    #identifier
    ids = xml.xpath('.//dc:identifier[@xsi:type="tel:ISBN"]', namespaces=ns)
    try:
        ids = ids[0].text
    except:
        ids = "N/A"
        
    #urn
    urn = xml.xpath('.//dc:identifier[@xsi:type="tel:URN"]', namespaces=ns)
    try:
        urn = urn[0].text
    except:
        urn = "N/A"
         
    meta_dict = {"IDN":idn, "CREATOR":creator, "TITLE":titel, "DATE":date, "PUBLISHER":publ, "URN":urn, "ISBN":ids}
    return meta_dict
  
    
                 
#Function für Titeldaten in MARC21
def parse_record_marc(item):

    ns = {"marc":"http://www.loc.gov/MARC21/slim"}
    xml = etree.fromstring(unicodedata.normalize("NFC", str(item)))
    
    #idn
    idn = xml.findall("marc:controlfield[@tag = '001']", namespaces=ns)
    try:
        idn = idn[0].text
    except:
        idn = 'N/A' 
        
    #creator
    creator1 = xml.findall("marc:datafield[@tag = '100']/marc:subfield[@code = 'a']", namespaces=ns)
    creator2 = xml.findall("marc:datafield[@tag = '110']/marc:subfield[@code = 'a']", namespaces=ns)
    subfield = xml.findall("marc:datafield[@tag = '110']/marc:subfield[@code = 'e']", namespaces=ns)
    
    if creator1:
        creator = creator1[0].text
    elif creator2:
        creator = creator2[0].text
        if subfield:
            creator = creator + " [" + subfield[0].text + "]"
    else:
        creator = "N/A"
    
    #Titel $a
    title = xml.findall("marc:datafield[@tag = '245']/marc:subfield[@code = 'a']", namespaces=ns)
    title2 = xml.findall("marc:datafield[@tag = '245']/marc:subfield[@code = 'b']", namespaces=ns)
    
    if title and not title2:
        titletext = title[0].text
    elif title and title2:     
        titletext = title[0].text + ": " + title2[0].text
    else:
        titletext = "N/A"
    
    #date
    date = xml.findall("marc:datafield[@tag = '264']/marc:subfield[@code = 'c']", namespaces=ns)
    try:
        date = date[0].text
    except:    
        date = 'N/A'
    
    #publisher
    publ = xml.findall("marc:datafield[@tag = '264']/marc:subfield[@code = 'b']", namespaces=ns)
    try:
        publ = publ[0].text
    except:    
        publ = 'N/A'
        
    #URN
    testurn = xml.findall("marc:datafield[@tag = '856']/marc:subfield[@code = 'x']", namespaces=ns)
    urn = xml.findall("marc:datafield[@tag = '856']/marc:subfield[@code = 'u']", namespaces=ns)
    
    if testurn:
        urn = urn[0].text
    else:    
        urn = 'N/A'
          
    #ISBN
    isbn_new = xml.findall("marc:datafield[@tag = '020']/marc:subfield[@code = 'a']", namespaces=ns)
    isbn_old = xml.findall("marc:datafield[@tag = '024']/marc:subfield[@code = 'a']", namespaces=ns)
    if isbn_new:
        isbn = isbn_new[0].text
    elif isbn_old: 
        isbn = isbn_old[0].text
    else:    
        isbn = 'N/A'
      
    meta_dict = {"IDN":idn, "CREATOR":creator, "TITLE": titletext, "DATE":date, 
                 "PUBLISHER":publ, "URN":urn, "ISBN":isbn}
    return meta_dict

                 
                 
             
#Funktion für Titeldaten in RDF:

def parse_record_rdf(record):
    
    ns = {"xlmns":"http://www.loc.gov/zing/srw/", 
          "agrelon":"https://d-nb.info/standards/elementset/agrelon#",
          "bflc":"http://id.loc.gov/ontologies/bflc/",
          "rdau":"http://rdaregistry.info/Elements/u/",
          "dc":"http://purl.org/dc/elements/1.1/",
          "rdau":"http://rdaregistry.info/Elements/u",
          "bibo":"http://purl.org/ontology/bibo/",
          "dbp":"http://dbpedia.org/property/",  
          "dcmitype":"http://purl.org/dc/dcmitype/", 
          "dcterms":"http://purl.org/dc/terms/", 
          "dnb_intern":"http://dnb.de/", 
          "dnbt":"https://d-nb.info/standards/elementset/dnb#", 
          "ebu":"http://www.ebu.ch/metadata/ontologies/ebucore/ebucore#", 
          "editeur":"https://ns.editeur.org/thema/", 
          "foaf":"http://xmlns.com/foaf/0.1/", 
          "gbv":"http://purl.org/ontology/gbv/", 
          "geo":"http://www.opengis.net/ont/geosparql#", 
          "gndo":"https://d-nb.info/standards/elementset/gnd#", 
          "isbd":"http://iflastandards.info/ns/isbd/elements/", 
          "lib":"http://purl.org/library/", 
          "madsrdf":"http://www.loc.gov/mads/rdf/v1#", 
          "marcrole":"http://id.loc.gov/vocabulary/relators/",
          "mo":"http://purl.org/ontology/mo/", 
          "owl":"http://www.w3.org/2002/07/owl#", 
          "rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#", 
          "rdfs":"http://www.w3.org/2000/01/rdf-schema#", 
          "schema":"http://schema.org/", 
          "sf":"http://www.opengis.net/ont/sf#", 
          "skos":"http://www.w3.org/2004/02/skos/core#", 
          "umbel":"http://umbel.org/umbel#", 
          "v":"http://www.w3.org/2006/vcard/ns#", 
          "vivo":"http://vivoweb.org/ontology/core#", 
          "wdrs":"http://www.w3.org/2007/05/powder-s#", 
          "xsd":"http://www.w3.org/2001/XMLSchema#"}
    
    xml = etree.fromstring(unicodedata.normalize("NFC", str(record)))
   
    #idn
    idn = xml.findall(".//dc:identifier", namespaces=ns)
    try:
        idn = idn[0].text
    except:
        idn = 'N/A' 
        
    #creator
    creator = record.find_all('rdau:p60327')
    
    try:
        creator = creator[0].text
    except:
        creator = "N/A"
        
    #title
    test = record.find_all('dc:title')
    
    try:
        test = test[0].text
    except:
        test = "N/A"
        
    #date
    date = record.find_all('dcterms:issued')
    try:
        date = date[0].text
    except:
        date = "N/A"    
      
    #publisher
    publ = record.find_all('dc:publisher')
    try:
        publ = publ[0].text
    except:
        publ = "N/A"    
    
    #urn
    urn = record.find_all('umbel:islike')
    try:
        urn = urn[0]
        urn = urn.get('rdf:resource')
    except:
        urn = "N/A"
    
    #isbn
    isbn = xml.findall(".//bibo:isbn13", namespaces=ns)
    isbn10 = xml.findall(".//bibo:isbn10", namespaces=ns)
    
    if isbn:
        isbn = isbn[0].text
    elif isbn10: 
        isbn = isbn10[0].text
    else:
        isbn = "N/A"
     
    meta_dict = {"IDN":idn, "CREATOR":creator, "TITLE":test, "DATE":date, "PUBLISHER":publ, "URN":urn, "ISBN":isbn}
    return meta_dict
                 
                 
#Funktion für GND in MARC21:

def parse_record_gndm(record):
    
    ns = {"xmlns":"http://www.loc.gov/MARC21/slim"}
    xml = etree.fromstring(unicodedata.normalize("NFC", str(record)))
    
    
    #Art
    gndtype = xml.findall("xmlns:datafield[@tag = '075']/xmlns:subfield[@code = 'b']", namespaces=ns)
    gndtype = gndtype[0].text
    
    if gndtype == "p": 
        gndtype = "Person"
    elif gndtype == "b":
        gndtype = "Organisation"
    elif gndtype == "u": 
        gndtype = "Werk"
    elif gndtype == "f": 
        gndtype = "Veranstaltung"
    elif gndtype == "g": 
        gndtype = "Geografikum" 
    elif gndtype == "n": 
        gndtype = "Person"
    elif gndtype == "s": 
        gndtype = "Sachbegriff"
        
        
    #Name
    main1 = xml.findall("xmlns:datafield[@tag = '100']/xmlns:subfield[@code = 'a']", namespaces=ns)
    main2 = xml.findall("xmlns:datafield[@tag = '110']/xmlns:subfield[@code = 'a']", namespaces=ns)
    main3 = xml.findall("xmlns:datafield[@tag = '111']/xmlns:subfield[@code = 'a']", namespaces=ns)
    main4 = xml.findall("xmlns:datafield[@tag = '130']/xmlns:subfield[@code = 'a']", namespaces=ns)
    main5 = xml.findall("xmlns:datafield[@tag = '150']/xmlns:subfield[@code = 'a']", namespaces=ns)
    main6 = xml.findall("xmlns:datafield[@tag = '151']/xmlns:subfield[@code = 'a']", namespaces=ns)
    
    
    if main1: 
        main = main1[0].text
    elif main2:     
        main = main2[0].text
    elif main3: 
        main = main3[0].text
    elif main4:
        main = main4[0].text
    elif main5:
        main = main5[0].text
    elif main6:
        main = main6[0].text
    else:
        main = "N/A"
        
    
    #title (bei Werken)
    title1 = xml.findall("xmlns:datafield[@tag = '100']/xmlns:subfield[@code = 't']", namespaces=ns)
    
    if title1: 
        title = title1[0].text
    else:
        title = 'N/A'
    
    
    
    #idn
    idn = xml.findall("xmlns:controlfield[@tag = '001']", namespaces=ns)
    try:
        idn = idn[0].text
    except:
        idn = 'N/A' 
    
    
    #Link
    link1 = xml.findall("xmlns:datafield[@tag = '024']/xmlns:subfield[@code = '0']", namespaces=ns)
    try:
        link1 = link1[0].text
    except:
        link1 = 'N/A' 
        
        
    
    dicty = {"IDN":idn, "TYPE":gndtype, "NAME":main, "TITLE":title, "LINK":link1}
    return dicty



#Funktion für GND in OAI-DC:

def parse_record_gndoai(record):
    
    ns = {"dc": "http://purl.org/dc/elements/1.1/", 
          "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
    xml = etree.fromstring(unicodedata.normalize("NFC", str(record)))
    
    
    #idn
    idn = xml.xpath(".//dc:identifier[@xsi:type='dnb:IDN']", namespaces=ns) #--> Adressiert das Element direkt   
    try:
        idn = idn[0].text
    except:
        idn = 'fail'
    
    
    #title
    title = xml.xpath(".//dc:title", namespaces=ns)  
    try:
        title = title[0].text
    except:
        title = 'N/A'   
    
    
    #creator
    creator = xml.xpath(".//dc:creator", namespaces=ns)  
    try:
        creator = creator[0].text
    except:
        creator = 'N/A'        
        
    
    dicty = {"IDN":idn, "NAME":creator, "TITLE":title}
    return dicty


#GND in RDF

def parse_record_gndrdf(record):
    
    ns = {"xlmns":"http://www.loc.gov/zing/srw/", 
          "agrelon":"https://d-nb.info/standards/elementset/agrelon#",
          "bflc":"http://id.loc.gov/ontologies/bflc/",
          "rdau":"http://rdaregistry.info/Elements/u/",
          "dc":"http://purl.org/dc/elements/1.1/",
          "rdau":"http://rdaregistry.info/Elements/u",
          "bibo":"http://purl.org/ontology/bibo/",
          "dbp":"http://dbpedia.org/property/",  
          "dcmitype":"http://purl.org/dc/dcmitype/", 
          "dcterms":"http://purl.org/dc/terms/", 
          "dnb_intern":"http://dnb.de/", 
          "dnbt":"https://d-nb.info/standards/elementset/dnb#", 
          "ebu":"http://www.ebu.ch/metadata/ontologies/ebucore/ebucore#", 
          "editeur":"https://ns.editeur.org/thema/", 
          "foaf":"http://xmlns.com/foaf/0.1/", 
          "gbv":"http://purl.org/ontology/gbv/", 
          "geo":"http://www.opengis.net/ont/geosparql#", 
          "gndo":"https://d-nb.info/standards/elementset/gnd#", 
          "isbd":"http://iflastandards.info/ns/isbd/elements/", 
          "lib":"http://purl.org/library/", 
          "madsrdf":"http://www.loc.gov/mads/rdf/v1#", 
          "marcrole":"http://id.loc.gov/vocabulary/relators/",
          "mo":"http://purl.org/ontology/mo/", 
          "owl":"http://www.w3.org/2002/07/owl#", 
          "rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#", 
          "rdfs":"http://www.w3.org/2000/01/rdf-schema#", 
          "schema":"http://schema.org/", 
          "sf":"http://www.opengis.net/ont/sf#", 
          "skos":"http://www.w3.org/2004/02/skos/core#", 
          "umbel":"http://umbel.org/umbel#", 
          "v":"http://www.w3.org/2006/vcard/ns#", 
          "vivo":"http://vivoweb.org/ontology/core#", 
          "wdrs":"http://www.w3.org/2007/05/powder-s#", 
          "xsd":"http://www.w3.org/2001/XMLSchema#"}
    
    xml = etree.fromstring(unicodedata.normalize("NFC", str(record)))
     
    #idn
    idn = xml.findall(".//gndo:gndidentifier", namespaces=ns)
    try:
        idn = idn[0].text
    except:
        idn = 'N/A' 
         
    #link
    link = record.find_all('rdf:description')
    try: 
        link = link[0]
        link = link.get('rdf:about')
    except:
        link = 'N/A' 
        
    #name
    name = record.find_all('gndo:preferrednamefortheperson')
    name2 = record.find_all('gndo:preferrednameforthecorporatebody') 
    name3 = record.find_all('gndo:preferrednameforthework') 
    name4 = record.find_all('gndo:preferrednamefortheconferenceorevent')
    name5 = record.find_all('gndo:preferrednameforthesubjectheading')
    
    if name:
        name = name[0].text
    elif name2:
        name = name2[0].text
    elif name3:
        name = name3[0].text
    elif name4: 
        name = name4[0].text
    elif name5: 
        name = name5[0].text
    else:
        name = "N/A"
        
    #time
    time = record.find_all('gndo:periodofactivity')
    time2 = record.find_all('gndo:dateofpublication')
    time3 = record.find_all('gndo:dateofconferenceorevent')
    time4 = record.find_all('gndo:dateofbirth')
    
    if time:
        time = time[0].text
    elif time2:
        time = time2[0].text
    elif time3:
        time = time3[0].text
    elif time4:
        time = time4[0].text + "-"
    else:
        time = "N/A"      
    
    #type
    gndtype = record.find_all('rdf:type')
    try: 
        gndtype = gndtype[0]
        gndtype = gndtype.get('rdf:resource')
    except:
        link = 'N/A' 
         
    meta_dict = {"IDN":idn, "NAME":name, "TIME":time, "LINK":link}
    return meta_dict


#Function für DMA in MARC21
def parse_record_dmamarc(item):

    ns = {"marc":"http://www.loc.gov/MARC21/slim"}
    xml = etree.fromstring(unicodedata.normalize("NFC", str(item)))
    
    #idn
    idn = xml.findall("marc:controlfield[@tag = '001']", namespaces=ns)
    try:
        idn = idn[0].text
    except:
        idn = 'N/A' 
        
    #creator
    creator1 = xml.findall("marc:datafield[@tag = '100']/marc:subfield[@code = 'a']", namespaces=ns)
    #creator2 = xml.findall("marc:datafield[@tag = '110']/marc:subfield[@code = 'a']", namespaces=ns)
    subfield = xml.findall("marc:datafield[@tag = '245']/marc:subfield[@code = 'c']", namespaces=ns)
    if creator1:
        creator = creator1[0].text
    elif subfield:
        creator = subfield[0].text
    else:
        creator = "N/A"
    
    #Titel $a
    title = xml.findall("marc:datafield[@tag = '245']/marc:subfield[@code = 'a']", namespaces=ns)
    title2 = xml.findall("marc:datafield[@tag = '245']/marc:subfield[@code = 'b']", namespaces=ns)
    
    if title and not title2:
        titletext = title[0].text
    elif title and title2:     
        titletext = title[0].text + ": " + title2[0].text
    else:
        titletext = "N/A"
    
    #Umfang/Format
    art = xml.findall("marc:datafield[@tag = '300']/marc:subfield[@code = 'a']", namespaces=ns)
    try:
        art = art[0].text
    except:    
        art = 'N/A'
     
    #date
    date = xml.findall("marc:datafield[@tag = '264']/marc:subfield[@code = 'c']", namespaces=ns)
    try:
        date = date[0].text
    except:    
        date = 'N/A'
    
    #publisher
    publ = xml.findall("marc:datafield[@tag = '264']/marc:subfield[@code = 'b']", namespaces=ns)
    try:
        publ = publ[0].text
    except:    
        publ = 'N/A'
          
    #ISBN
    isbn_new = xml.findall("marc:datafield[@tag = '020']/marc:subfield[@code = 'a']", namespaces=ns)
    isbn_old = xml.findall("marc:datafield[@tag = '024']/marc:subfield[@code = 'a']", namespaces=ns)
    if isbn_new:
        isbn = isbn_new[0].text
    elif isbn_old: 
        isbn = isbn_old[0].text
    else:    
        isbn = 'N/A'
    
    meta_dict = {"IDN":idn, "CREATOR":creator, "TITLE":titletext, "DATE":date, "PUBLISHER":publ, "ISBN":isbn}  
    return meta_dict



#Funktion für DMA in OAI-DC
def parse_record_dmadc(record):
    
    ns = {"dc": "http://purl.org/dc/elements/1.1/", 
          "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
    xml = etree.fromstring(unicodedata.normalize("NFC", str(record)))
    
    #idn
    idn = xml.xpath(".//dc:identifier[@xsi:type='dnb:IDN']", namespaces=ns) #--> Adressiert das Element direkt   
    try:
        idn = idn[0].text
    except:
        idn = 'fail'
    
    #creator:
    creator = xml.xpath('.//dc:creator', namespaces=ns)
    try:
        creator = creator[0].text
    except:
        creator = "N/A"
    
    #titel
    titel = xml.xpath('.//dc:title', namespaces=ns)
    try:
        titel = titel[0].text
    except:
        titel = "N/A"
        
    #date
    date = xml.xpath('.//dc:date', namespaces=ns)
    try:
        date = date[0].text
    except:
        date = "N/A"
    
    #publisher
    publ = xml.xpath('.//dc:publisher', namespaces=ns)
    try:
        publ = publ[0].text
    except:
        publ = "N/A"
    
    #format
    form = xml.xpath('.//dc:format', namespaces=ns)
    try:
        form = form[0].text
    except:
        form = "N/A"
                
        
    meta_dict = {"IDN":idn, "CREATOR":creator, "TITLE":titel, "DATE":date, "PUBLISHER":publ, "FORMAT":form}
    return meta_dict


#DMA in RDF: 

def parse_record_dmardf(record):
    
    ns = {"xlmns":"http://www.loc.gov/zing/srw/", 
          "agrelon":"https://d-nb.info/standards/elementset/agrelon#",
          "bflc":"http://id.loc.gov/ontologies/bflc/",
          "rdau":"http://rdaregistry.info/Elements/u/",
          "dc":"http://purl.org/dc/elements/1.1/",
          "rdau":"http://rdaregistry.info/Elements/u",
          "bibo":"http://purl.org/ontology/bibo/",
          "dbp":"http://dbpedia.org/property/",  
          "dcmitype":"http://purl.org/dc/dcmitype/", 
          "dcterms":"http://purl.org/dc/terms/", 
          "dnb_intern":"http://dnb.de/", 
          "dnbt":"https://d-nb.info/standards/elementset/dnb#", 
          "ebu":"http://www.ebu.ch/metadata/ontologies/ebucore/ebucore#", 
          "editeur":"https://ns.editeur.org/thema/", 
          "foaf":"http://xmlns.com/foaf/0.1/", 
          "gbv":"http://purl.org/ontology/gbv/", 
          "geo":"http://www.opengis.net/ont/geosparql#", 
          "gndo":"https://d-nb.info/standards/elementset/gnd#", 
          "isbd":"http://iflastandards.info/ns/isbd/elements/", 
          "lib":"http://purl.org/library/", 
          "madsrdf":"http://www.loc.gov/mads/rdf/v1#", 
          "marcrole":"http://id.loc.gov/vocabulary/relators/",
          "mo":"http://purl.org/ontology/mo/", 
          "owl":"http://www.w3.org/2002/07/owl#", 
          "rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#", 
          "rdfs":"http://www.w3.org/2000/01/rdf-schema#", 
          "schema":"http://schema.org/", 
          "sf":"http://www.opengis.net/ont/sf#", 
          "skos":"http://www.w3.org/2004/02/skos/core#", 
          "umbel":"http://umbel.org/umbel#", 
          "v":"http://www.w3.org/2006/vcard/ns#", 
          "vivo":"http://vivoweb.org/ontology/core#", 
          "wdrs":"http://www.w3.org/2007/05/powder-s#", 
          "xsd":"http://www.w3.org/2001/XMLSchema#"}
    
    xml = etree.fromstring(unicodedata.normalize("NFC", str(record)))
     
    #idn
    idn = xml.findall(".//dc:identifier", namespaces=ns)
    try:
        idn = idn[0].text
    except:
        idn = 'N/A' 
              
    #creator
    name = record.find_all('rdau:p60327')
    
    if name:
        name = name[0].text
    else:
        name = "N/A"
        
    #title:
    title = record.find_all('dc:title')
    
    if title:
        title = title[0].text
    else: 
        title = "N/A"
        
    #publisher
    publ = record.find_all('dc:publisher')
        
    if publ:
        publ = publ[0].text
    else:
        publ = "N/A"
    
    #date
    time = record.find_all('dcterms:issued')
        
    if time:
        time = time[0].text
    else:
        time = "N/A"
          
    meta_dict = {"IDN":idn, "NAME":name, "TITLE":title, "PUBLISHER":publ, "DATE":time}
    return meta_dict

                 
## -----------------------------------------------------------------------------
                 
def table():     
    #Titeldaten:
    if auswahl == "DNB" and dataform == "oai_dc":
        result = [parse_record_dc(record) for record in records]
        df = pandas.DataFrame(result)  
    elif auswahl == "DNB" and dataform == "MARC21-xml":
        result2 = [parse_record_marc(item) for item in records_marc]
        df = pandas.DataFrame(result2)      
    elif auswahl == "DNB" and dataform == "RDFxml":
        result3 = [parse_record_rdf(item) for item in records]
        df = pandas.DataFrame(result3)    

    #GND:
    elif auswahl == "GND" and dataform == "MARC21-xml":
        result4 = [parse_record_gndm(item) for item in gndm]
        df = pandas.DataFrame(result4)                            
    elif auswahl == "GND" and dataform == "oai_dc":
        result5 = [parse_record_gndoai(item) for item in records]
        df = pandas.DataFrame(result5)
        st.write('Bitte beachten Sie, dass sich das Format "DNB Casual (oai_dc)" nur bedingt für GND-Datensätze eignet.')
        st.write('Für eine Darstellung mit mehr Informationen wählen Sie bitte das Format "MARC21-xml".')
    elif auswahl == "GND" and dataform == "RDFxml":
        result6 = [parse_record_gndrdf(item) for item in records]
        df = pandas.DataFrame(result6)     
        
    #DMA:
    elif auswahl == "DMA" and dataform == "MARC21-xml":
        result7 = [parse_record_dmamarc(item) for item in records_marc]
        df = pandas.DataFrame(result7)                           
    elif auswahl == "DMA" and dataform == "oai_dc":
        result8 = [parse_record_dmadc(record) for record in records]
        df = pandas.DataFrame(result8)
    elif auswahl == "DMA" and dataform == "RDFxml":
        result9 = [parse_record_dmardf(record) for record in records]
        df = pandas.DataFrame(result9)
    
    else:
        st.write("Es wurde noch keine Suchanfrage gestellt.")
        
    return df


def downclick(): 
    st.session_state.downclick += 1


#Ausgaben:             

if confirm and not searchterm:
    st.write(" ")
elif confirm and searchterm:

    st.markdown("##### Ausgeben und Speichern der Daten:")
    
    st.info("Bitte beachten Sie: Ein Klick auf einen der Download-Buttons setzt die Anzeige zurück. Um die Anzeige und Downloadmöglichkeiten weiterhin zu "
            "nutzen, klicken Sie einfach erneut auf 'Los!' und führen Ihre Suche noch einmal aus.") 

    st.download_button(
        label="Download XML",
        data=r1.text,
        file_name='data.xml',
        mime='text/xml',
        #key='letsgo',
        #on_click='table()',
    )
               
    st.markdown("##### Darstellung als Tabelle:")
    
    df = table()
    
    #st.session_state["df"]=df 
    st.dataframe(df)

    def convert_df(df): 
        return df.to_csv().encode('utf-8')
    
    
    ## Download CSV: 
    st.download_button(
        label="Download CSV",
        data=convert_df(df),
        file_name='Tabelle.csv',
        mime='text/csv',
        #on_click=downclick(),
    )
    #st.write(st.session_state.downclick)
else:
    st.write(" ")
    
st.write(" ")
    
if st.session_state.downclick != 0:
    st.write("Button wurde bereits geklickt")
    st.session_state["df"]

    
    #if st.session_state.letsgo == 1:
        #df['result'] = df['data'] + a
        #st.dataframe(df)

     
        
        
footer="""<style>
        .footer {
left: 0;
bottom: 0;
width: 100%;
text-align: center;
}
</style>
<div class="footer">
<br><br><br>
<p>Zuletzt aktualisiert am: 01.03.2022</a></p>
</div>
"""

st.markdown(footer,unsafe_allow_html=True)
