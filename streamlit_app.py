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

# with header: 
#     st.title('Ball Mayhem')
#     st.header('Which Ad Frequency hits better revenue? ')
#     # st.text('time 1500') #time stamp to check if streamlit web app is updated
#     st.text(' ')

# with analysis:
#     connection = sqlite3.connect('database.db') 
#     st.subheader('Let us take a look at the data we have. ')
#     st.write(df.head(10))

#     s1, s2 = st.columns(2)

#     #show platform ratio
#     query = '''
#     SELECT platform, count(platform) FROM case_table
#     GROUP BY platform
#     '''
#     f = pd.read_sql_query(query, connection)
#     fig, ax = plt.subplots()
#     ax.pie(f['count(platform)'], labels=f['platform'], autopct='%1.1f%%')
#     ax.set_title('Platform Distribution')
#     s1.pyplot(fig)

#     #show total session by user
#     query = '''
#     SELECT user_id, SUM(session_length) as length
#     FROM case_table
#     GROUP BY user_id
#     ORDER BY length DESC
#     '''
#     f = pd.read_sql_query(query, connection)
#     fig, ax = plt.subplots()
#     ax.hist(f['length'], bins=50)
#     ax.set_xlabel('Total Session Length')
#     ax.set_ylabel('Count')
#     ax.set_title('Distribution of Total Session Length per User')
#     s2.pyplot(fig)

#     st.text(' ') #end

# with dashboard: 
#     connection = sqlite3.connect('database.db') 
#     st.subheader('We have tested with 6 different ad frequencies and here are some of the results for discussions. ')

#     st.text(' ')
#     ad_freq_options = ['control', 'xxLow', 'xLow', 'xHigh', 'gameTune', 'xxHigh']
#     ad_freq = st.selectbox('The ad frequency is', ad_freq_options)
#     st.text('1: control, 2: xxLow, 3: xLow, 4: xHigh, 5: gameTune, 6: xxHigh')
    
#     query = '''
#     SELECT user_id, ab_cohort_name,
#         SUBSTR(open_at, 12, 2) AS hour_of_day,
#         total_revenue
#     FROM
#         (SELECT user_id,
#                 ab_cohort_name,
#                 SUM(publisher_revenue) AS total_revenue,
#                 open_at
#             FROM case_table
#             GROUP BY user_id, ab_cohort_name, open_at) AS user_cohort_revenue
#     GROUP by user_id, ab_cohort_name, hour_of_day
#     '''
#     f = pd.read_sql_query(query, connection)
#     new_f = f[f['ab_cohort_name'] == ad_freq]

#     sns.set_style("whitegrid")
#     fig, ax = plt.subplots(figsize=(12, 6))
#     sns.barplot(
#         x="hour_of_day", 
#         y="total_revenue", 
#         hue="ab_cohort_name",
#         data=new_f,
#         ax=ax,
#     )
#     ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

#     ax.set_xlabel("Hour of Day")
#     x_labels = ['{}'.format(str(hour).zfill(2)) for hour in range(24)]
#     ax.set_xticklabels(x_labels, rotation=45, ha='right')
#     ax.set_ylabel("Total revenue")
#     ax.set_title("Total revenue of selected ad frequency by the hour of the day")
#     st.pyplot(fig)

#     hour_mapping = {
#     0: '00', 1: '01', 2: '02', 3: '03', 4: '04', 5: '05', 6: '06', 7: '07',
#     8: '08', 9: '09', 10: '10', 11: '11', 12: '12', 13: '13', 14: '14', 15: '15',
#     16: '16', 17: '17', 18: '18', 19: '19', 20: '20', 21: '21', 22: '22', 23: '23'}
#     hour_value = st.slider('The hour you are interested in is ', min_value = 0, max_value = 23, value = 0, step = 1)
#     hour_select = hour_mapping[hour_value]
#     st.write(hour_select)
#     new_f2 = f[f['hour_of_day'] == hour_select]

#     sns.set_style("whitegrid")
#     fig, ax = plt.subplots(figsize=(12, 6))
#     sns.barplot(
#         x="hour_of_day", 
#         y="total_revenue", 
#         hue="ab_cohort_name",
#         data=new_f2,
#         ax=ax,
#     )
#     ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

#     ax.set_xlabel("Hour of Day")
#     ax.set_ylabel("Total revenue")
#     ax.set_title("Total revenue by ad frequency at selected hour of the day")
#     st.pyplot(fig)
