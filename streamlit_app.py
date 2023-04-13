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
