import streamlit as st
import pandas as pd
import numpy as np

# Make sure the paths for the csv files are correct
df_year = pd.read_csv('Calendar-Years.csv')
df_year = df_year[df_year['Activity'] == 'Cycle']
df_year = df_year[['Year','Ascent (feet)','Calories']]
# Fix the year value so it doesn't have a thousands comma in it
df_year['Year'] = df_year['Year'].astype(str)
df_year['Year'] = df_year['Year'].str.replace(',', '', regex=False)

df_month = pd.read_csv('Calendar-Months.csv')
df_month = df_month[df_month['Activity'] == 'Cycle']
df_month = df_month[['Month','Ascent (feet)','Calories']]

df_week = pd.read_csv('Calendar-Weeks.csv')
df_week = df_week[df_week['Activity'] == 'Cycle']
df_week = df_week[['Week','Ascent (feet)','Calories']]


st.header(":blue[Cyclemeter data since going batshit for MTB]")

st.subheader("Feet climbed and calories burned by year")
st.line_chart(df_year, x="Year")

st.subheader("Feet climbed and calories burned by month")
st.line_chart(df_month, x="Month")

st.subheader("Feet climbed and calories burned by week")
st.line_chart(df_week, x="Week")


st.subheader("The pandas dataframes:")
st.markdown("Yearly")
st.write(df_year)
st.markdown("Monthly")
st.write(df_month)
st.markdown("Weekly")
st.write(df_week)
