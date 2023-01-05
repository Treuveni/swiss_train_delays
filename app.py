import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio
import altair as alt
import os

pio.templates.default = "plotly_white"

st.title('SBB Verspätungsanalyse')
st.write('Die foldgenden Grafiken zeigen Analysen zur Verspätung von Zügen zwischen 3.11.2022 und 31.12.22.\nDashboard erstellt von: Tamara Reuveni Mazig || Datenquellen: opentransportdata.swiss, data.sbb.ch')

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
df = pd.read_parquet(os.path.join(__location__, 'data.parquet'))

st.sidebar.write('## Daten filtern')
hours = st.sidebar.slider(label = 'Uhrzeit', min_value=0, max_value=23, value = (6,22))
abroad_choice = st.sidebar.multiselect(label="Ursprung (Erste Haltestelle)", options=['Schweiz','Ausland'],default=['Schweiz','Ausland'])
type_choice = st.sidebar.multiselect(label="Zuggattung", options=df['Zuggattung'].unique(),default=df['Zuggattung'].unique())


df = df[(df.Stunde.between(hours[0], hours[1])) & (df.Ursprung.isin(abroad_choice)) & (df.Zuggattung.isin(type_choice))]


station_counts=df.groupby(['Haltestelle','lat','long','Datum'])['Linie'].count().reset_index().groupby(['Haltestelle','lat','long'])['Linie'].mean().reset_index()
station_counts = station_counts.merge(df.groupby('Haltestelle')['Ist verspätet'].mean().round(2), right_index=True, left_on = 'Haltestelle', how='left')

fig = px.scatter_geo(data_frame=station_counts, 
        lon = station_counts['long'],
        lat = station_counts['lat'],
        hover_data = {'Haltestelle':True, 'lat':False, 'long':False, 'Linie':False},
        color = station_counts['Ist verspätet'], 
        opacity = 0.5, 
        size = station_counts['Linie'],
        fitbounds = False)

fig.update_layout(
    #    title = 'Most trafficked US airports<br>(Hover for airport names)',
        autosize=False,
        height=400,
        width =700, 
        margin = dict(t=30, r=0, l=0, b=0),
        template ="plotly",  
        geo = dict(
        scope ='europe',
        resolution = 50,
        projection_scale = 23,
        projection_type = 'boggs',
        center = dict(lat=46.8153, lon=8.2275),
        
    ))


st.subheader('Anteil verspätete Züge pro Haltestelle')
st.write('Die Grösse der Blase repräsentiert die durchschnittliche tägliche Anzahl Züge pro Haltestelle.')
st.plotly_chart(fig, use_container_width=True, theme="streamlit")
# data = data.loc[:100000, :]
# st.write(data.head(10))


mpd = df.groupby(['Zuggattung','Datum'])['Linie'].count().reset_index().groupby('Zuggattung')['Linie'].mean().reset_index().round(0)
mpd.columns = ['Zuggattung','Züge pro Tag']

st.subheader('Durchschnittliche Anzahl Züge pro Tag per Zuggattung')

c_pie = alt.Chart(mpd).mark_arc(innerRadius =80).encode(
    theta=alt.Theta(field="Züge pro Tag", type="quantitative"),
    color=alt.Color(field="Zuggattung", type="nominal",  sort=alt.EncodingSortField('Züge pro Tag', order='descending')),
    order = alt.Order(field= "Züge pro Tag", type="quantitative", sort="descending")
).properties(
    width=350,
    height=300)
st.altair_chart(c_pie, theme='streamlit')

model_df = df.groupby('Zuggattung')['Ist verspätet'].mean().reset_index().round(2)
model_df.columns = ['Zuggattung','Anteil Verspätungen']
st.subheader('Durchschnittliche Verspätung pro Zuggattung')
#st.bar_chart(model_df['Verspätung'])
c_bar = alt.Chart(model_df).mark_bar().encode(x='Anteil Verspätungen:Q', y=alt.Y('Zuggattung:N', sort='x'))
st.altair_chart(c_bar, use_container_width=True, theme = 'streamlit')


hourly_df = df.groupby('Stunde')['Verspätungskategorie'].value_counts()
hourly_df.name = 'Anzahl Züge'
hourly_df = hourly_df.reset_index()
st.subheader('Durchschnittliche Anzahl verspätete Züge pro Stunde')
c_area = alt.Chart(hourly_df).mark_area().encode(x='Stunde:Q', y='Anzahl Züge:Q', color='Verspätungskategorie:N')
st.altair_chart(c_area, use_container_width =True, theme = 'streamlit')

