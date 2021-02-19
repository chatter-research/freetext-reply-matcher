import ast
import pandas as pd
import streamlit as st
from match import Matcher

@st.cache
def get_data(file):
    if file:
        df = pd.read_csv(file)
        return df.reply.values
    return None

# Threshold widget
threshold = st.sidebar.slider(
    label='Select the match score threshold:',
    min_value=50,
    max_value=100,
    value=80,
    step=1
)

# Input widget for categories
default_categories = {'category_name': ['variant_1', 'variant_2']}

categories = st.sidebar.text_area(
    label='Enter the categories:',
    value=default_categories,
    height=500
)
categories = ast.literal_eval(categories)

# File uploader widget
file = st.sidebar.file_uploader("Upload the CSV to match:")
strings_to_match = get_data(file)

#if st.button('Start matching!'):
@st.cache
def do_matching():
    matcher = Matcher(categories=categories, threshold=threshold)
    results = matcher.run(queries=strings_to_match, limit=1)
    df = matcher.get_results_df()
    return matcher, df

matcher, df = do_matching()

filter_selection = st.radio(
    label='Filter results',
    options=('Show all', 'Show matches only', 'Show unmatched only')
)
if filter_selection == 'Show matches only':
    df = df.query('matched_category!="no_match"')
elif filter_selection == 'Show unmatched only':
    df = df.query('matched_category=="no_match"')
else:
    pass
st.write(df)
st.success('Done matching!')
