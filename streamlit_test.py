import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

# generate some sample data
data = pd.DataFrame({
    'x': np.arange(10),
    'y': np.random.rand(10)
})

# define the chart
chart = alt.Chart(data).mark_bar().encode(
    x='x',
    y='y'
).interactive()

# create a selection that chooses the nearest point & selects based on lasso selection
selector = alt.selection(type='single', nearest=True, on='mouseover',
                         encodings=['x'], empty='none')

# create a lasso selection that selects points based on a lasso selection
lasso = alt.selection(type='interval', encodings=['x'])

# add a layer of points to highlight selected points
highlight = chart.mark_point().encode(
    x='x',
    y='y',
    opacity=alt.condition(selector | lasso, alt.value(1), alt.value(0))
)

# add a layer of text for the values being displayed
text = chart.mark_text(align='left', baseline='middle').encode(
    x='x',
    y='y',
    text='y'
).transform_filter(selector)

# create a streamlit app
st.title('Bar Chart with Lasso Select')

# display the chart with selection and highlight
st.altair_chart((chart + highlight).properties(width=600, height=400).add_selection(selector, lasso), use_container_width=True)

# display the selected x-axis values
selected_x_values = [data.iloc[int(np.round(event['x']))]['x'] for event in chart.selection.values()]
st.write('Selected x-axis values:', selected_x_values)
