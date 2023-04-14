import streamlit as st 
import pandas as pd
import sqlite3
import altair as alt

st.set_page_config(page_title = 'Retail Sales Analysis',
                   layout='wide',
                   initial_sidebar_state='collapsed')

# Define the containers
header = st.container()
kpis = st.container()
analysis = st.container()
dashboard = st.container()
trend_line = st.container()

@st.cache_data
def get_data():
    df = pd.read_csv('clean_data.csv')
    # Convert the transaction date column to datetime format
    df['tran_date'] = pd.to_datetime(df['tran_date'])

    # Extract the year and month from the transaction date
    df['year'] = df['tran_date'].dt.year
    df['month'] = df['tran_date'].dt.month
    
   # df['Age'] = df['Age'].astype(int)
    
    return df

df = get_data()

# Define the header section
with header:
    st.title('Retail Sales Analysis')
    st.subheader('Visualizing seasonal trends in average order value')
    st.markdown('---')

with st.sidebar:
    
    country_filter = st.multiselect(label= 'Select the country',
                                options=df['city_code'].unique(),
                                default=df['city_code'].unique())
    
    year_select = st.radio(label= 'Select the required year (single select)',
                                options=df['year'].unique())
    
    store_filter = st.multiselect(label= 'Select the store type',
                                options=df['Store_type'].unique(),
                                default=df['Store_type'].unique())
    
    # display the slider
    age_range = st.slider("Select age range", min_value=int(df['Age'].min()), max_value=int(df['Age'].max()), 
                          value=(int(df['Age'].min()), int(df['Age'].max())))

    
# filter the data based on the user selection
filtered_data = df[(df['city_code'].isin(country_filter)) & (df['year']==year_select) & 
                   (df['Store_type'].isin(store_filter)) & (df['Age'].between(age_range[0], age_range[1]))]

# calculate the KPI values for filtered data
filtered_sales = filtered_data['total_amt'].sum()
filtered_quantity = filtered_data['Qty'].sum()
filtered_customers = filtered_data['customer_Id'].nunique()
    
col1, col2, col3 = st.columns(3)

# calculate the KPI values
total_sales = df['total_amt'].sum()
total_quantity = df['Qty'].sum()
total_customers = df['customer_Id'].nunique()

# display the KPIs in the container
with kpis:
    st.subheader('KPIs Section Analysis')

    col1.metric("Total Sales", f"€ {filtered_sales/1000000:,.2f}M / € {total_sales/1000000:,.2f}M")
    col2.metric("Total Quantity", f"{filtered_quantity:,.0f} / {total_quantity:,.0f}")
    col3.metric("Distinct # of Customers", f"{filtered_customers:,.0f} / {total_customers:,.0f}")
    
    st.markdown('---')

with trend_line:  
  
    st.subheader('Trend Analysis of AoV')
  
    # Calculate the AOV for each month
    aov_monthly = filtered_data.groupby(['prod_cat', 'year', 'month'])['total_amt'].sum().reset_index()
    
    # Create an Altair chart with a dropdown menu and a tooltip
    aov_chart = alt.Chart(aov_monthly).mark_line(interpolate='basis').encode(
        x='month:N',
        y=alt.Y('total_amt:Q', axis=alt.Axis(title='Total Sales (in €)')),
        color='prod_cat:N',
        tooltip=['prod_cat:N', 'month:N', 'total_amt:Q']
        ).properties(
        width=700,
        height=400, # Change the height as per your requirement
        title='Seasonality of Total Sales'
    )

    # Render the chart using Streamlit's Altair chart renderer
    st.altair_chart(aov_chart)

#     # Create an Altair chart with a dropdown menu and a tooltip
#     aov_chart = alt.Chart(aov_monthly).mark_line().encode(
#         x='month:N',
#         y=alt.Y('total_amt:Q', axis=alt.Axis(title='Total Sales (in €)')),
#         color='prod_cat:N',
#         tooltip=['prod_cat:N', 'month:N', 'total_amt:Q']
#     ).properties(
#         title='Seasonality of Total Sales'
#     )
    
#     # Render the chart using Streamlit's Altair chart renderer
#     st.altair_chart(aov_chart)
    
    st.markdown('---')

    
#chart1,chart2 = st.columns(2)
#    st.markdown('---')

# Define the dashboard section
# with dashboard:
#     st.subheader('Dashboard')
#     st.write('This section provides an interactive dashboard to explore the data.')
#     st.markdown('---')

# with kpis:
#     st.subheader('KPIs Section Analysis')
# #    st.write('This section provides a detailed analysis of the data.')
  
#     def get_data():
#       df = pd.read_csv('clean_data.csv') 
#       return df

#     df = get_data()

#     df1 = df.query('campaign == @Campaign_filter')

#     total_amount = float(df1['total_amt'].sum())
#     average_aov = float(df1['AOV'].mean())
#     total_qty = float(df1['Qty'].sum())
#     #total_conversions= float(df1['Total_Conversion'].sum()) 
#     #total_approved_conversions = float(df1['Approved_Conversion'].sum())

#     total_amount,average_aov,total_qty = st.columns(3,gap='large')
    
# # Define the analysis section
# with analysis:
#     st.subheader('Data Analysis')
#     st.write('This section provides a detailed analysis of the data.')
    
#     def get_data():
#     df = pd.read_csv('clean_data.csv')
#     connection = sqlite3.connect('database.db')
#     df.to_sql('case_table', connection, if_exists='replace')    
#     return df

#     df = get_data()
    
    
    
#     year_filter = st.sidebar.radio('Select year:', df['year'].unique().tolist())
    
#     # Filter the data based on the year filter    
#     df = df[df['year'] == year_filter]
    
#     # Calculate the AOV for each month
#     aov_monthly = df.groupby(['prod_cat', 'year', 'month']).mean().reset_index()

#     # Create a selection tool for the year
# #     year_select = alt.selection_single(
# #         name='Year',
# #         fields=['year'],
# #         bind=alt.binding_select(options=aov_monthly['year'].unique().tolist())
# #     )

#     # Create an Altair chart with a dropdown menu and a tooltip
#     aov_chart = alt.Chart(aov_monthly).mark_line().encode(
#         x='month:N',
#         y=alt.Y('AOV:Q', axis=alt.Axis(title='Average Order Value')),
#         color='prod_cat:N',
#         tooltip=['prod_cat:N', 'month:N', 'AOV:Q']
#     ).properties(
#         title='Seasonality of Average Order Value'
#     )

#     # Render the chart using Streamlit's Altair chart renderer
#     st.altair_chart(aov_chart)


