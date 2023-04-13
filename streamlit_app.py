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

@st.cache
def get_data():
    df = pd.read_csv('clean_data.csv')
    
    connection = sqlite3.connect('database.db')
    df.to_sql('case_table', connection, if_exists='replace')    
    return df

df = get_data()
