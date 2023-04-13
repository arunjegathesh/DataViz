import streamlit as st 
import pandas as pd
import sqlite3
import altair as alt

st.set_page_config(page_title = 'Retail Sales Analysis',
                   layout='wide',
                   initial_sidebar_state='collapsed')

# Define the containers
header = st.container()
analysis = st.container()
dashboard = st.container()

# Define the header section
with header:
    st.title('Retail Sales Analysis')
    st.subheader('Visualizing seasonal trends in average order value')
    st.markdown('---')
    
with st.sidebar:
    Campaign_filter = st.multiselect(label= 'Select The country',
                                options=df['city_code'].unique(),
                                default=df['city_code'].unique())

df1 = df.query('campaign == @Campaign_filter')

total_amount = float(df1['total_amt'].sum())
average_aov = float(df1['AOV'].mean())
total_qty = float(df1['Qty'].sum())
#total_conversions= float(df1['Total_Conversion'].sum()) 
#total_approved_conversions = float(df1['Approved_Conversion'].sum())


total_amount,average_aov,total_qty = st.columns(3,gap='large')
    
# Define the analysis section
with analysis:
    st.subheader('Data Analysis')
    st.write('This section provides a detailed analysis of the data.')

    # Load the data
    @st.cache_data
    def get_data():
        df = pd.read_csv('clean_data.csv')
        connection = sqlite3.connect('database.db')
        df.to_sql('case_table', connection, if_exists='replace')    
        return df

    df = get_data()
    
    # Convert the transaction date column to datetime format
    df['tran_date'] = pd.to_datetime(df['tran_date'])

    # Extract the year and month from the transaction date
    df['year'] = df['tran_date'].dt.year
    df['month'] = df['tran_date'].dt.month
    
    year_filter = st.sidebar.radio('Select year:', df['year'].unique().tolist())
    
    # Filter the data based on the year filter    
    df = df[df['year'] == year_filter]
    
    # Calculate the AOV for each month
    aov_monthly = df.groupby(['prod_cat', 'year', 'month']).mean().reset_index()

    # Create a selection tool for the year
#     year_select = alt.selection_single(
#         name='Year',
#         fields=['year'],
#         bind=alt.binding_select(options=aov_monthly['year'].unique().tolist())
#     )

    # Create an Altair chart with a dropdown menu and a tooltip
    aov_chart = alt.Chart(aov_monthly).mark_line().encode(
        x='month:N',
        y=alt.Y('AOV:Q', axis=alt.Axis(title='Average Order Value')),
        color='prod_cat:N',
        tooltip=['prod_cat:N', 'month:N', 'AOV:Q']
    ).properties(
        title='Seasonality of Average Order Value'
    )

    # Render the chart using Streamlit's Altair chart renderer
    st.altair_chart(aov_chart)

# Define the dashboard section
with dashboard:
    st.subheader('Dashboard')
    st.write('This section provides an interactive dashboard to explore the data.')
    st.markdown('---')
