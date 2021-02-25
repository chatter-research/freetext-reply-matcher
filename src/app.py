import ast
import pandas as pd
import streamlit as st
from match import Matcher


def main():
    # Set up the sidebar
    df, threshold, categories = create_sidebar()
    # Prompt user to complete all steps
    if (df is None) or (categories is None):
        st.info('Please complete all steps on the left to start')
    else:
        df_result = do_matching(df, categories, threshold)
        match_ratio, no_match_ratio = calculate_ratio(df_result)
        st.success(f'Done matching! {match_ratio:.1%} replies matched, {no_match_ratio:.1%} unmatched.')
        # Radio widget for filtering results
        filter_selection = st.radio(
            label='Filter results',
            options=('Show all', 'Show matches only', 'Show unmatched only'),
            index=2
        )
        if filter_selection == 'Show matches only':
            df_show = df_result.query('matched_category!="no_match"')
        elif filter_selection == 'Show unmatched only':
            df_show = df_result.query('matched_category=="no_match"')
        else:
            df_show = df_result.copy()
        if st.button('Shuffle results'):
            df_show = df_show.sample(frac=1)
        st.write(df_show)


@st.cache
def get_df(file):
    if file:
        df = pd.read_csv(file)
        # Filter out null values
        df = df.loc[~df.reply.isnull(), :]
        return df
    return None


@st.cache
def do_matching(df, categories, threshold):
    matcher = Matcher(categories=categories, threshold=threshold)
    matcher.run(queries=df.reply.values, limit=1)
    # Create a new column for the matches
    df_result = df.copy()
    df_result['matched_category'] = matcher.results_list
    df_result = df_result[['reply_id', 'reply', 'matched_category']]
    return df_result


def calculate_ratio(df_result):
    # Calculate the match ratios
    no_match_ratio = (df_result.matched_category=='no_match').mean()
    match_ratio = 1 - no_match_ratio
    return match_ratio, no_match_ratio


def create_sidebar():
    st.sidebar.title('Freetext Reply Matcher')

    # File uploader widget
    file = st.sidebar.file_uploader("STEP 1 - Upload the CSV file:")
    df = get_df(file)
    #st.write(f'df: {df}')
    # Threshold widget
    threshold = st.sidebar.slider(
        label='STEP 2 - Select the match score threshold:',
        min_value=50,
        max_value=100,
        value=80,
        step=1
    )

    # Input widget for categories
    #default_categories = {'category_name': ['variant_1', 'variant_2']}
    categories = st.sidebar.text_area(
        label='STEP 3 - Enter the categories:',
        value=None,
        height=500
    )
    categories = ast.literal_eval(categories)
    #st.write(f'categories: {categories}')
    return df, threshold, categories


if __name__ == "__main__":
    main()
