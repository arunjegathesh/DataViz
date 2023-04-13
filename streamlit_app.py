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

# Convert the transaction date column to datetime format
df['tran_date'] = pd.to_datetime(df['tran_date'])

# Extract the year and month from the transaction date
df['year'] = df['tran_date'].dt.year
df['month'] = df['tran_date'].dt.month

# Calculate the AOV for each month
aov_monthly = df.groupby(['prod_cat', 'month']).mean().reset_index()
#aov_monthly = df.groupby(['year', 'month'])['AOV'].mean().reset_index()

# Create an Altair chart
# Create a selection tool for the year
prod_cat_select = alt.selection_single(
    name='Prod',
    fields=['prod_cat'],
    bind=alt.binding_select(options=aov_monthly['prod_cat'].unique().tolist())
)

# Create an Altair chart with a dropdown menu and a tooltip
aov_chart = alt.Chart(aov_monthly).mark_line().encode(
    x='month:N',
    y=alt.Y('AOV:Q', axis=alt.Axis(title='Average Order Value')),
    color='prod_cat:N',
    tooltip=['prod_cat:N', 'month:N', 'AOV:Q']
).add_selection(year_select).transform_filter(prod_cat_select).properties(
    title='Seasonality of Average Order Value'
)

# # Render the chart using Streamlit's Altair chart renderer
st.altair_chart(aov_chart)

