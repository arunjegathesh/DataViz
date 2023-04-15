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

st.set_page_config(page_title = 'Retail Sales Analysis',
                   layout='wide',
                   initial_sidebar_state='collapsed')

# Define the containers
header = st.container()
kpis = st.container()
map_plot = st.container()
trend_line = st.container()
bar_plot = st.container()
spinner_cont = st.container()

@st.cache_data
def get_data():
    df = pd.read_csv('clean_data.csv')
    
    df['tran_date'] = pd.to_datetime(df['tran_date'])

    df['year'] = df['tran_date'].dt.year
    df['month'] = df['tran_date'].dt.strftime('%b')    
    return df

df = get_data()


#st.success('Done!')
# Define the header section
with header:
    st.title('Retail Sales Analysis')
#    st.subheader('Visualizing seasonal trends in average order value')
    st.markdown('---')

with st.sidebar:

    country_filter = st.multiselect(label= 'Select the region',
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

    with col1:
      st.image('flaticons/money-bag.png',use_column_width='True', width=150)
      #st.metric(label = 'Total Impressions', value= numerize(total_impressions))
      st.metric("Total Sales", f"€ {filtered_sales/1000000:,.2f}M / € {total_sales/1000000:,.2f}M")

    with col2:
      st.image('flaticons/shopping-cart.png',use_column_width='True', width=150)
      #st.metric(label = 'Total Impressions', value= numerize(total_impressions))
      st.metric("Total Quantity", f"{filtered_quantity:,.0f} / {total_quantity:,.0f}")

    with col3:
      st.image('flaticons/people.png',use_column_width='True', width=150)
      #st.metric(label = 'Total Impressions', value= numerize(total_impressions))
      st.metric("# of Customers", f"{filtered_customers:,.0f} / {total_customers:,.0f}")

    st.write("Each KPI representing a quick summary of the top metrics from the overall data. This structure aids the any user of the dashboard to get up-to-speed with the business status with a quick glance. Dynamic metrics that show the current selections' data while also showing the overall picture.")

    #col3.metric("Distinct # of Customers", f"{filtered_customers:,.0f} / {total_customers:,.0f}")
    st.markdown('---')

geo_in = get_data()

geo_df = geo_in[
                   #(geo_in['city_code'].isin(country_filter)) &
                   (geo_in['year']==year_select) & 
#                  (geo_in['Gender'] == gender_filter[0]) &
                   (geo_in['Store_type'].isin(store_filter)) & (geo_in['Age'].between(age_range[0], age_range[1]))]

city_counts = geo_df.groupby(['year', 'city_code'])['total_amt'].sum().reset_index()
city_counts.columns = ['year', 'city_code', 'Total Revenue (€)']

regions_geojson = 'https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions.geojson'
regions_gdf = gpd.read_file(regions_geojson)
regions_gdf.columns = ['code', 'city_code','geometry']
regions_gdf.at[0,'city_code']='Paris'
regions_gdf.at[7,'city_code']='Brittany'
regions_gdf.at[12,'city_code']='Corsica'
# Duplicate the first row
row_to_duplicate = regions_gdf.iloc[0:1]
regions_gdf = pd.concat([regions_gdf, row_to_duplicate], ignore_index=True)
# Reset the index of the new DataFrame
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

      #geo_filtered = merged_gdf[merged_gdf['year'] == year_select]

      #geo_filtered = geo_df

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
#                             hover_data={'Total Revenue (€)': True})
                             hover_data={'Total Revenue (€)': ':,.3r K'})

   #   fig.update_traces(hovertemplate='Total Revenue (€): %{hovertext}<extra></extra>')

      st.plotly_chart(fig, use_container_width=True, height=1000)
      st.write("This map is a wonderful representation of France")

      st.markdown('---')

with trend_line:  

    st.subheader('What trend or seasonality can we observe from yearly data?')

    aov_monthly = filtered_data.groupby(['prod_cat', 'year', 'month'])['AOV'].mean().reset_index()

#     tooltip = ['prod_cat:N (Product Category)', 'month:N (Month)', 'AOV:Q (Average Order Value)']
#     new_labels = {'prod_cat': 'Product Category', 'month': 'Month', 'AOV': 'Average Order Value'}
    tooltip = [alt.Tooltip('prod_cat:N', title='Product Category'),alt.Tooltip('month:N', title='Month'),alt.Tooltip('AOV:Q', title='Average Order Value (€)', format='.2f')]

    aov_chart = alt.Chart(aov_monthly).mark_line(point=True).encode(
        x=alt.X('month:N', sort=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], axis=alt.Axis(title='Month')),
        y=alt.Y('AOV:Q', axis=alt.Axis(title='Average Order Value (€)')),
        color=alt.Color('prod_cat:N', legend=alt.Legend(title='Product Category')),
#         tooltip= ['prod_cat:N', 'month:N', 'AOV:Q']
        tooltip = tooltip
        ).properties(
        width=1200,
        height=400 # Change the height as per your requirement
#         title='Seasonality of Average Order Value across Product Categories'
    ).interactive()

    # Render the chart using Streamlit's Altair chart renderer
    st.altair_chart(aov_chart)

    st.markdown('---')

with bar_plot: 
    col1, col2 = st.columns(2)
    with col1:  
        st.subheader('Males vs Females! Who shops more?')

        sales_by_subcat = filtered_data.groupby(['prod_subcat', 'Gender'])['total_amt'].sum().reset_index()

    #    label_data = filtered_data.groupby(['prod_subcat'])['total_amt'].sum().reset_index()

        tooltip = [alt.Tooltip('total_amt:N', title='Total Amount (€)', format='.2f'),alt.Tooltip('Gender:N', title='Gender')]

#         # Format y-axis labels as thousands
#         y_axis = alt.Axis(title='Total Amount (€)', format='~s')

#         # Add data labels to the top of the bars
#         text = alt.Chart(label_data).mark_text(dy=-5, color='black').encode(
#                x=alt.X('prod_subcat', sort='-y', axis=alt.Axis(title='Product Sub-Category',labelAngle=315,labelFontSize=8, labelLimit=80)),
#                y=alt.Y('total_amt:Q', axis=y_axis, stack=False),
#                text=alt.Text('total_amt:Q', format='0,.3s'))

        color_scale = alt.Scale(domain=['F', 'M'], range=['#666EF6', '#B54B36'])
        bar_chart = alt.Chart(sales_by_subcat).mark_bar().encode(
                    x=alt.X('prod_subcat', sort='-y',axis=alt.Axis(title='Product Sub-Category',labelAngle=315,labelFontSize=8, labelLimit=80)),
                    y=alt.Y('total_amt:Q', axis=alt.Axis(title='Total Amount (€)', format = '~s')),
                    color=alt.Color('Gender:N', scale=color_scale),
                    #column=alt.Column('Gender:N', header=alt.Header(title=None, labels=False)),
                    tooltip=tooltip).properties(
                    width=600,
                    height=600 # Change the height as per your requirement
    #                 title='Spread of sales across Product Sub Categories'
                     ).interactive()
#         color_scale = alt.Scale(domain=['F', 'M'], range=['#666EF6', '#B54B36'])

#         bar_chart = alt.Chart(sales_by_subcat).mark_bar().encode(
#             x=alt.X('Gender:N', axis=alt.Axis(title='Gender')),
#             y=alt.Y('total_amt:Q', axis=alt.Axis(title='Total Amount (€)', format='~s')),
#             color=alt.Color('Gender:N', scale=color_scale),
#             column=alt.Column('prod_subcat:N', header=alt.Header(labelAngle=-90, labelAlign='right')),
#             tooltip=tooltip
#         ).properties(
#             width=800,
#             height=600
#         ).configure_view(
#             stroke='transparent'
#         ).interactive()
    
#         bar_chart = bar_chart.configure_view(
#                 stroke='transparent'
#             ).configure_axisX(
#                 labelAngle=-45,
#                 labelAlign='right',
#                 labelFontSize=8,
#                 labelLimit=100,
#                 titleY=35
#             ).configure_view(
#                 continuousWidth=300
#             )
        
#        chart = bar_chart + text

        st.altair_chart(bar_chart)

    with col2:
        st.subheader('Lets scout the categories radar!')

        grouped_df = filtered_data.groupby(['prod_cat', 'Gender']).sum().reset_index()

        # Create a radar chart using Plotly Express
        fig = px.line_polar(grouped_df, r='Qty', theta='prod_cat', color='Gender',
                          line_close=True, labels={'prod_cat': 'Product Category', 'Qty': 'Quantity'}, template='plotly_dark')

        fig.update_layout(#title=f'Sum of Quantities by Product Category and Gender',
                        polar=dict(radialaxis=dict(visible=True, range=[0, grouped_df['Qty'].max()],color='white')))
        #                       paper_bgcolor='black')

        # Display the radar chart
        st.plotly_chart(fig)

# with bar_plot:  

#     st.subheader('Bar Chart bla bla')

#     sales_by_subcat = filtered_data.groupby(['prod_subcat', 'Gender'])['total_amt'].sum().reset_index()

#     # calculate the total sales by subcategory
#     total_sales_by_subcat = filtered_data.groupby('prod_subcat')['total_amt'].sum().reset_index()
#     total_sales_by_subcat = total_sales_by_subcat.rename(columns={'total_amt': 'total_sales'})

#     # sort the subcategories by total sales
#     sales_by_subcat = sales_by_subcat.merge(total_sales_by_subcat, on='prod_subcat')
#     sales_by_subcat = sales_by_subcat.sort_values(['total_sales', 'prod_subcat'], ascending=[False, True])

#     # format the total_amt values as thousands
#     sales_by_subcat['total_amt'] = '€ ' + (sales_by_subcat['total_amt'] / 1000).astype(int).apply(lambda x: '{:,}'.format(x)) + ' K'

#     # plot the bar chart with data labels
#     bar_chart = alt.Chart(sales_by_subcat).mark_bar().encode(
#         x=alt.X('prod_subcat:N', sort='-y', axis=alt.Axis(title='Product Sub-Category', labelAngle=315, labelFontSize=8, labelLimit=80)),
#         y=alt.Y('total_amt:Q', axis=alt.Axis(title='Total Amount (€)')),
#         color=alt.Color('Gender:N', legend=alt.Legend(title="Gender")),
#         tooltip=[alt.Tooltip('total_amt:N', title='Total Amount (€)', format='.2f'), alt.Tooltip('Gender:N', title='Gender')],
#         text=alt.Text('total_amt:Q', format='.1s')
#     ).properties(
#         width=1200,
#         height=600, # Change the height as per your requirement
#         title='Spread of sales across Product Sub Categories'
#     ).configure_axis(
#         labelFontSize=12,
#         titleFontSize=14
#     ).configure_title(
#         fontSize=18
#     )

#     # format the y-axis labels as thousands
#     bar_chart.encoding.y.axis.format = 's'

#     st.altair_chart(bar_chart, use_container_width=True)

    st.markdown('---')
  
# with spider_plot:

#     st.subheader('Lets scout the categories radar!')

#     grouped_df = filtered_data.groupby(['prod_cat', 'Gender']).sum().reset_index()

#     # Create a radar chart using Plotly Express
#     fig = px.line_polar(grouped_df, r='Qty', theta='prod_cat', color='Gender',
#                         line_close=True, labels={'prod_cat': 'Product Category', 'Qty': 'Quantity'}, template='plotly_dark')

#     fig.update_layout(#title=f'Sum of Quantities by Product Category and Gender',
#                       polar=dict(radialaxis=dict(visible=True, range=[0, grouped_df['Qty'].max()],color='white')))
# #                       paper_bgcolor='black')

#     # Display the radar chart
#     st.plotly_chart(fig)

#     st.markdown('---')




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

