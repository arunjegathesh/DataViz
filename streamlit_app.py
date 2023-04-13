import streamlit as st 
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt

st.set_page_config(page_title = 'Retail Sales Analysis',
                    layout='wide',
                    initial_sidebar_state='collapsed')

header = st.container()
analysis = st.container()
dashboard = st.container()

@st.cache_data
def get_data():
    df = pd.read_csv('clean_data.csv')
    
    connection = sqlite3.connect('database.db')
    df.to_sql('case_table', connection, if_exists='replace')    
    return df

df = get_data()

# Import required libraries
import altair as alt

# Create a new dataframe with 'tran_date', 'AOV', and 'prod_cat' columns
df_trend = df[['tran_date', 'AOV', 'prod_cat']].copy()

# Convert 'tran_date' column to datetime format
df_trend['tran_date'] = pd.to_datetime(df_trend['tran_date'], infer_datetime_format=True, errors='coerce')

# Extract month from 'tran_date' column and create a new column 'month'
df_trend['month'] = df_trend['tran_date'].dt.month

# Group by 'prod_cat' and 'month' columns and calculate the mean of 'AOV'
df_trend = df_trend.groupby(['prod_cat', 'month']).mean().reset_index()

# # Define a chart object with 'tran_date' as x-axis and 'AOV' as y-axis
# chart = alt.Chart(df_trend).mark_line().encode(
#     x=alt.X('tran_date', axis=alt.Axis(format='%d-%m-%Y')),
#     y=alt.Y('AOV', title='Average Order Value'),
#     color='prod_cat'
# ).properties(
#     width=600,
#     height=400
# )

# # Render the chart using Streamlit's Altair chart renderer
# st.altair_chart(chart)

