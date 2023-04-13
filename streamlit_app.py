import streamlit as st 
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

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

# Create a new dataframe with 'tran_date', 'AOV', and 'prod_cat' columns
df_trend = df[['tran_date', 'AOV', 'prod_cat']].copy()

# # Convert 'tran_date' column to datetime format
df_trend['tran_date'] = pd.to_datetime(df_trend['tran_date'], infer_datetime_format=True, errors='coerce')

# # Extract month from 'tran_date' column and create a new column 'month'
# df_trend['month'] = df_trend['tran_date'].dt.month

# # Group by 'prod_cat' and 'month' columns and calculate the mean of 'AOV'
# df_trend = df_trend.groupby(['prod_cat', 'month']).mean().reset_index()

# # Create a FacetGrid object with 'prod_cat' column for different subplots
# g = sns.FacetGrid(df_trend, col="prod_cat", col_wrap=3)

# # Map a line plot with 'tran_date' as x-axis and 'AOV' as y-axis on each subplot
# g.map(sns.lineplot, 'tran_date', 'AOV')

# # Set the title for each subplot
# for ax in g.axes.flat:
#     ax.set_title(ax.get_title().replace("prod_cat = ", "Product Category: "))

# # Convert FacetGrid object to matplotlib figure object
# fig = g.fig

# # Convert the matplotlib figure object to Streamlit pyplot object
# st.pyplot(fig)

