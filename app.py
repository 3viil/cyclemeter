import streamlit as st
import pandas as pd
import numpy as np

df_year = pd.read_csv('Calendar-Years.csv')
df_year = df_year[df_year['Activity'] == 'Cycle']
df_year = df_year[['Year','Ascent (feet)','Calories','Distance (miles)']]
df_year['Climb/distance ratio'] = df_year['Ascent (feet)'] / df_year['Distance (miles)']
# Convert years into str and then modify to a format that to_datetime recognizes
df_year['Year'] = df_year['Year'].astype(str)
df_year['Year'] = df_year['Year'] + '-01-01'
df_year['Year'] = pd.to_datetime(df_year['Year'])

df_month = pd.read_csv('Calendar-Months.csv')
df_month = df_month[df_month['Activity'] == 'Cycle']
df_month = df_month[['Month','Ascent (feet)','Calories','Distance (miles)']]
df_month['Climb/distance ratio'] = df_month['Ascent (feet)'] / df_month['Distance (miles)']
df_month['Month'] = df_month['Month'] + '-01'
df_month['Month'] = pd.to_datetime(df_month['Month'])

df_week = pd.read_csv('Calendar-Weeks.csv')
df_week = df_week[df_week['Activity'] == 'Cycle']
df_week = df_week[['Week','Ascent (feet)','Calories','Distance (miles)']]
df_week['Climb/distance ratio'] = df_week['Ascent (feet)'] / df_week['Distance (miles)']
df_week['Week'] = pd.to_datetime(df_week['Week'])


st.header(":blue[Cyclemeter MTB Data, 2011-2025]")

st.subheader("Data by Year")
tab1, tab2, tab3 = st.tabs(["Ascent & Calories", "Ascent/distance ratio", "Dataframe"])
tab1.line_chart(df_year, x="Year", y = ['Ascent (feet)','Calories'], height=400)
tab2.line_chart(df_year, x="Year", y = "Climb/distance ratio", height=400)
tab3.dataframe(df_year, height=400, use_container_width=True)

st.subheader("Data by Month")
tab1, tab2, tab3 = st.tabs(["Ascent & Calories", "Ascent/distance ratio", "Dataframe"])
tab1.line_chart(df_month, x="Month", y = ['Ascent (feet)','Calories'], height=400)
tab2.line_chart(df_month, x="Month", y = "Climb/distance ratio", height=400)
tab3.dataframe(df_month, height=400, use_container_width=True)

st.subheader("Data by Week")
tab1, tab2, tab3 = st.tabs(["Ascent & Calories", "Ascent/distance ratio", "Dataframe"])
tab1.line_chart(df_week, x="Week", y = ['Ascent (feet)','Calories'], height=400)
tab2.line_chart(df_week, x="Week", y = "Climb/distance ratio", height=400)
tab3.dataframe(df_week, height=400, use_container_width=True)
