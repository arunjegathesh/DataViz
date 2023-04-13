import streamlit as st 
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

header = st.container()
analysis = st.container()
dashboard = st.container()

#Caching the data for faster loading
@st.cache_data
# def get_data():
#     df = pd.read_csv('Voodoo_Test_Business_Case.csv', sep=';')

#     #fill in mode for missing values in countries 
#     mode = df['country'].mode().to_list()[0]
#     df['country'] = df['country'].fillna(mode)

#     connection = sqlite3.connect('database.db')
#     df.to_sql('case_table', connection, if_exists='replace')
#     return df

# df = get_data()

with header: 
    st.title('Ball Mayhem')
    st.header('Which Ad Frequency hits better revenue? ')
    # st.text('time 1500') #time stamp to check if streamlit web app is updated
    st.text(' ')

# with analysis:
#     connection = sqlite3.connect('database.db') 
#     st.subheader('Let us take a look at the data we have. ')
#     st.write(df.head(10))
