import streamlit as st 
import pandas as pd
import sqlite3
import altair as alt
import pygal 
import base64
import numpy as np
import plotly.express as px
import geopandas as gpd

st.set_page_config(page_title = 'Retail Sales Analysis',
                   layout='wide',
                   initial_sidebar_state='collapsed')

# Define the containers
header = st.container()
kpis = st.container()
trend_line = st.container()
bar_plot = st.container()
spider_plot = st.container()
map_plot = st.container()

@st.cache_data
def get_data():
    df = pd.read_csv('clean_data.csv')
    
    df['tran_date'] = pd.to_datetime(df['tran_date'])

    df['year'] = df['tran_date'].dt.year
    df['month'] = df['tran_date'].dt.strftime('%b')    
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
                                options=np.sort(df['year'].unique()).tolist())
    
    store_filter = st.multiselect(label= 'Select the store type',
                                options=df['Store_type'].unique(),
                                default=df['Store_type'].unique())

    age_range = st.slider("Select age range", min_value=int(df['Age'].min()), max_value=int(df['Age'].max()), 
                          value=(int(df['Age'].min()), int(df['Age'].max())))

# filter the data based on the user selection
filtered_data = df[(df['city_code'].isin(country_filter)) & 
                   (df['year']==year_select) & 
#                  (df['Gender'] == gender_filter[0]) &
                   (df['Store_type'].isin(store_filter)) & (df['Age'].between(age_range[0], age_range[1]))]

# calculate the KPI values for filtered data
filtered_sales = filtered_data['total_amt'].sum()
filtered_quantity = filtered_data['Qty'].sum()
filtered_customers = filtered_data['customer_Id'].nunique()
    
#col1, col2, col3 = st.columns(3)

# calculate the KPI values
total_sales = df['total_amt'].sum()
total_quantity = df['Qty'].sum()
total_customers = df['customer_Id'].nunique()

# display the KPIs in the container
with kpis:
    st.subheader('KPIs Section Analysis')
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Total Sales", f"€ {filtered_sales/1000000:,.2f}M / € {total_sales/1000000:,.2f}M")
    col2.metric("Total Quantity", f"{filtered_quantity:,.0f} / {total_quantity:,.0f}")
    col3.metric("Distinct # of Customers", f"{filtered_customers:,.0f} / {total_customers:,.0f}")
    st.markdown('---')

with trend_line:  
  
    st.subheader('Trend Analysis of AoV')
  
    aov_monthly = filtered_data.groupby(['prod_cat', 'year', 'month'])['AOV'].mean().reset_index()
    
    aov_chart = alt.Chart(aov_monthly).mark_line().encode(
        x=alt.X('month:N', sort=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
        y=alt.Y('AOV:Q', axis=alt.Axis(title='Average Order Value (in €)')),
        color='prod_cat:N',
        tooltip=['prod_cat:N', 'month:N', 'AOV:Q']
        ).properties(
        width=1200,
        height=400, # Change the height as per your requirement
        title='Seasonality of Average Order Value across Product Categories'
    )

    # Render the chart using Streamlit's Altair chart renderer
    st.altair_chart(aov_chart)
    
    st.markdown('---')
    
with bar_plot:  
  
    st.subheader('Bar Chart bla bla')

    sales_by_subcat = filtered_data.groupby(['prod_subcat', 'Gender'])['total_amt'].sum().reset_index()

    bar_chart = alt.Chart(sales_by_subcat).mark_bar().encode(
        x=alt.X('prod_subcat', sort='-y'),
        y='total_amt:Q',
        color='Gender:N',
        tooltip=['prod_subcat:N', 'total_amt:N', 'Gender:N']).properties(
        width=1200,
        height=400, # Change the height as per your requirement
        title='Spread of sales across Product Sub Categories')
    
    st.altair_chart(bar_chart)
    
    st.markdown('---')

with spider_plot:

    grouped_df = filtered_data.groupby(['prod_cat', 'Gender']).sum().reset_index()

    # Create a radar chart using Plotly Express
    fig = px.line_polar(grouped_df, r='Qty', theta='prod_cat', color='Gender',
                        line_close=True, template='plotly_white')

    fig.update_layout(title=f'Sum of Quantities by Product Category and Gender',
                      polar=dict(radialaxis=dict(visible=True, range=[0, grouped_df['Qty'].max()],color='black')),
                      paper_bgcolor='black')
  
    # Display the radar chart
    st.plotly_chart(fig)
    
    st.markdown('---')
    
def get_geo_data():
    df = pd.read_csv('merged_gdf.csv')
    
#     df['tran_date'] = pd.to_datetime(df['tran_date'])

#     df['year'] = df['tran_date'].dt.year
#     df['month'] = df['tran_date'].dt.strftime('%b')    
    return df

geo_df = get_geo_data()

with map_plot:  
  
    st.subheader('map chart bla bla')

    geo_filtered = geo_df[geo_df['Year'] == year_select]

    # Define the mapbox style and center
    mapbox_style = "open-street-map"
    mapbox_center = {"lat": 46.2276, "lon": 2.2137}

    # Define the bounds for Europe
    bounds = [[-27.070207, -34.276938], [75.0599, 60.238064]]

# Create a choropleth map with Plotly
    fig = px.choropleth_mapbox(geo_filtered,
                           geojson=geo_filtered.geometry,
                           locations=geo_filtered.index,
                           color='Transaction Count',
                           color_continuous_scale='blues',
                           mapbox_style=mapbox_style,
                           zoom=3, center=mapbox_center,
                           hover_name='city_code',
                           hover_data={'Transaction Count': True})

    st.plotly_chart(fig)
    
    st.markdown('---')


# # Create a sidebar container for the city selection
# with st.sidebar:
#     # Add a dropdown menu to select the city
#     city_dropdown = st.selectbox('Select a city:', df['city_code'].unique())

# Add a button to update the chart when the city is changed
# if st.button('Update Chart'):
#     update_chart(city_dropdown)

# # Display the initial radar chart
# update_chart(df['city_code'].unique()[0])
    
# def render_svg(svg):
#     """Renders the given svg string."""
#     b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
#     html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
#     st.write(html, unsafe_allow_html=True)

# with spider_plot:  
  
#     st.subheader('With great power comes great responsibility')    
#     grouped_df = filtered_data.groupby(['prod_cat', 'Gender'])['Qty'].sum().reset_index()

#     # Reshape the dataframe to a wide format
#     pivoted_df = grouped_df.pivot_table(index='prod_cat', columns='Gender', values='Qty')
    
#     radar_chart = pygal.Radar(show_legend=True, tooltip_border_radius=10, tooltip_font_size=15, style=pygal.style.LightGreenStyle)
#     radar_chart.title = f'Sum of Quantities by Product Category and Gender'
#     radar_chart.x_labels = pivoted_df.index.tolist()
#     radar_chart.add('Male', pivoted_df['M'].tolist())
#     radar_chart.add('Female', pivoted_df['F'].tolist())
    
# #    st.pygal_chart(radar_chart)
 
#     chart = radar_chart.render()
#     # Convert SVG chart to PNG
#     st.write('### SVG Output')
#     render_svg(chart)
    
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

