import streamlit as st 
import pandas as pd
import sqlite3
import altair as alt
import pygal 
import base64
import numpy as np
import plotly.express as px
import geopandas as gpd
import time
import streamlit as st
import plotly.express as px
import json

st.set_page_config(page_title = 'Retail Sales Analysis',
                   layout='wide',
                   initial_sidebar_state='collapsed')

# Define the containers
header = st.container()
kpis = st.container()
map_plot = st.container()
trend_line = st.container()
bar_plot = st.container()
spider_plot = st.container()
test_cont = st.container()

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
    
    st.markdown('---')

with st.sidebar:

    country_filter = st.multiselect(label= 'Select the required region (multiselect)',
                                options=df['city_code'].unique(),
                                default=df['city_code'].unique())

    year_select = st.radio(label= 'Select the required year (single select)',
                                options=np.sort(df['year'].unique()).tolist())

    store_filter = st.multiselect(label= 'Select the store type (multiselect)',
                                options=df['Store_type'].unique(),
                                default=df['Store_type'].unique())

    age_range = st.slider("Select age range using the slider", min_value=int(df['Age'].min()), max_value=int(df['Age'].max()), 
                          value=(int(df['Age'].min()), int(df['Age'].max())))

    # Create a calendar object in the sidebar
    selected_dates = st.date_input("Select a date range from the Transaction Date",
                                    [(df["tran_date"]).min(),
                                    (df["tran_date"]).max()],
                                    key="date_range")


mask = (df['city_code'].isin(country_filter)) & (df['year'] == year_select) & (
    df['Store_type'].isin(store_filter)) & (df['Age'].between(age_range[0], age_range[1]))
filtered_data = df.loc[mask].loc[((df["tran_date"]) >= pd.to_datetime(selected_dates[0])) & (
        (df["tran_date"]) <= pd.to_datetime(selected_dates[1]))]

# # filter the data based on the user selection
# filtered_data = df[(df['city_code'].isin(country_filter)) & 
#                    (df['year']==year_select) &
#                    (df['Store_type'].isin(store_filter)) & (df['Age'].between(age_range[0], age_range[1]))]

# calculate the KPI values for filtered data
filtered_sales = filtered_data['total_amt'].sum()
filtered_quantity = filtered_data['Qty'].sum()
filtered_customers = filtered_data['customer_Id'].nunique()

# calculate the KPI values
total_sales = df['total_amt'].sum()
total_quantity = df['Qty'].sum()
total_customers = df['customer_Id'].nunique()

# display the KPIs in the container
with kpis:
    st.subheader('KPIs Section Analysis')
    col1, col2, col3 = st.columns(3)

    with col1:
      st.image('flaticons/money-bag.png',use_column_width='True', width=150)
      st.metric("Total Sales", f"€ {filtered_sales/1000000:,.2f}M / € {total_sales/1000000:,.2f}M")

    with col2:
      st.image('flaticons/shopping-cart.png',use_column_width='True', width=150)
      st.metric("Total Quantity", f"{filtered_quantity:,.0f} / {total_quantity:,.0f}")

    with col3:
      st.image('flaticons/people.png',use_column_width='True', width=150)
      st.metric("# of Customers", f"{filtered_customers:,.0f} / {total_customers:,.0f}")

    st.write("Each KPI representing a quick summary of the top metrics from the overall data. This structure aids the any user of the dashboard to get up-to-speed with the business status with a quick glance. Dynamic metrics that show the current selections' data while also showing the overall picture.")
    
    st.markdown('---')

# geo_in = get_data()

# geo_df = geo_in[(df['city_code'].isin(country_filter)) & 
#                 (geo_in['year']==year_select) & 
#                 (geo_in['Store_type'].isin(store_filter)) & 
#                 (geo_in['Age'].between(age_range[0], age_range[1]))]

geo_df = filtered_data

city_counts = geo_df.groupby(['year', 'city_code'])['total_amt'].sum().reset_index()
city_counts.columns = ['year', 'city_code', 'Total Revenue (€)']

regions_geojson = 'https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions.geojson'
regions_gdf = gpd.read_file(regions_geojson)
regions_gdf.columns = ['code', 'city_code','geometry']
regions_gdf.at[0,'city_code']='Paris'
regions_gdf.at[7,'city_code']='Brittany'
regions_gdf.at[12,'city_code']='Corsica'


row_to_duplicate = regions_gdf.iloc[0:1]
regions_gdf = pd.concat([regions_gdf, row_to_duplicate], ignore_index=True)

regions_gdf = regions_gdf.reset_index(drop=True)
regions_gdf.at[13,'city_code']='Créteil'

def get_geometry(row):
    if row['city_code'] in city_counts['city_code'].unique():
        return regions_gdf.loc[regions_gdf['city_code'] == row['city_code'], 'geometry'].iloc[0]

geo_df['geometry'] = geo_df.apply(get_geometry, axis=1)

# Join the transaction data to the GeoPandas DataFrame based on city names
merged_gdf = regions_gdf.merge(city_counts, on='city_code', how='left')
merged_gdf.dropna(subset=['Total Revenue (€)'], inplace=True)

with map_plot:  

      st.subheader('Where do rich people live in France?')

      geo_filtered = merged_gdf

      # Define the mapbox style and center
      mapbox_style = "open-street-map"
      mapbox_center = {"lat": 46.2276, "lon": 2.2137}

      # Define the bounds for Europe
      bounds = [[-27.070207, -34.276938], [75.0599, 60.238064]]

  # Create a choropleth map with Plotly
      fig = px.choropleth_mapbox(geo_filtered,
                             geojson=geo_filtered.geometry,
                             locations=geo_filtered.index,
                             color='Total Revenue (€)',
                             color_continuous_scale='blues',
                             mapbox_style=mapbox_style,
                             zoom=3, center=mapbox_center,
                             hover_name='city_code',
                             hover_data={'Total Revenue (€)': ':,.3r K'})

      st.plotly_chart(fig, use_container_width=True, height=1000)

      city_list = st.session_state.get('state', {}).get('city_code', [])

      st.write(city_list)
      
      st.write("Introducing our interactive addition for analysis - a heatmap UI! With its intuitive color-coding and data visualization, one can easily spot trends, patterns, and make data-driven decisions. For tracking overall trend of sales our heatmap UI is a powerful tool to take our data analysis to the next level.")
      st.markdown('---')

with trend_line:  

    st.subheader('What trend or seasonality can we observe from yearly data?')

    aov_monthly = filtered_data.groupby(['prod_cat', 'year', 'month'])['AOV'].mean().reset_index()

    tooltip = [alt.Tooltip('prod_cat:N', title='Product Category'),alt.Tooltip('month:N', title='Month'),alt.Tooltip('AOV:Q', title='Average Order Value (€)', format='.2f')]

    aov_chart = alt.Chart(aov_monthly).mark_line(point=True).encode(
        x=alt.X('month:N', sort=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], axis=alt.Axis(title='Month')),
        y=alt.Y('AOV:Q', axis=alt.Axis(title='Average Order Value (€)')),
        color=alt.Color('prod_cat:N', legend=alt.Legend(title='Product Category')),
        tooltip = tooltip
        ).properties(
        width=1200,
        height=400).interactive()

    st.altair_chart(aov_chart)

    st.write("Discover the power of trend analysis with our website's latest feature - a visual representation of average order value across product categories over time. With our easy-to-use tool, we can track and compare sales trends over months to make data-driven decisions about the business performance across different product categories.")

    st.markdown('---')

with bar_plot: 
    st.subheader('Males vs Females! Who shops more?')

    sales_by_subcat = filtered_data.groupby(['prod_subcat', 'Gender'])['total_amt'].sum().reset_index()

    tooltip = [alt.Tooltip('prod_subcat:N', title='Product Sub Category'),
               alt.Tooltip('Gender:N', title='Gender'),
               alt.Tooltip('total_amt:N', title='Total Amount (€)', format='0,.3s')]

    color_scale = alt.Scale(domain=['F', 'M'], range=['#666EF6', '#B54B36'])
    bar_chart = alt.Chart(sales_by_subcat).mark_bar(width = 22).encode(
              column=alt.Column('prod_subcat:N', header=alt.Header(title=None, labels=True,orient='bottom',
                                                                   labelAngle=0,labelFontSize=9.5, labelLimit=80),
                                sort=alt.EncodingSortField(field='total_amt', op='sum', order='descending')),
              x=alt.X('Gender:N', sort='-y',axis=alt.Axis(ticks=False, labels=False, title='')),
              y=alt.Y('total_amt:Q', axis=alt.Axis(grid=False, title='Total Amount (€)', format = '~s')),
              color=alt.Color('Gender:N', scale=color_scale),
              tooltip=tooltip).configure_view(
              stroke=None, width = 45).interactive()
    st.altair_chart(bar_chart)
    
    st.write('Introducing the next feature - a grouped bar visualization that showcases purchasing behavior between male and female customers across various product sub-categories. This intuitive visualization makes it easy to identify buying patterns and preferences between genders, allowing us to make informed decisions about the product offerings. From identifying popular products to creating targeted marketing campaigns, our grouped bar visualization is a key tool for any retail website.')
    st.markdown('---')

with spider_plot:
    st.subheader('Lets scout the categories radar!')

    grouped_df = filtered_data.groupby(['prod_cat', 'Gender']).sum().reset_index()

    fig = px.line_polar(grouped_df, r='Qty', theta='prod_cat', color='Gender',
                      line_close=True, labels={'prod_cat': 'Product Category', 'Qty': 'Quantity'}, template='plotly_dark')

    fig.update_layout(#title=f'Sum of Quantities by Product Category and Gender',
                    polar=dict(radialaxis=dict(visible=True, range=[0, grouped_df['Qty'].max()],color='white')))

    st.plotly_chart(fig, use_container_width=True, height=800)
    
    st.write('Take the retail sales analysis to the next level with a radar chart UI. This powerful visualization tool allows us to compare multiple metrics across product categories and genders, giving a multi-level view of the retail performance. With its intuitive design and interactive features, our radar chart UI makes it easy to identify trends and make data-driven decisions. Whether we are looking to optimize our marketing strategy or identify areas for growth, our radar chart UI is the perfect solution for any data-driven analysis.')

    st.markdown('---')
             
st.markdown('[Images Source : Flaticon](https://www.flaticon.com)', unsafe_allow_html=True)
