import pandas as pd


# CONFIGS
USEFUL_COLS = ['anime_id', 'title', 'type', 'episodes', 
               'duration', 'genres', 'start_date', 'end_date']
SHOUNEN_TAG = 'Shounen'
SLICE_OF_LIFE_TAG = 'Slice of Life'
BINARY_CATEGORY_PREFIX = 'is_'

def filter_cols(df, columns_to_keep=USEFUL_COLS):
    """
    Keeps only the columns we need for the analysis.
    """
    missing_cols = [col for col in columns_to_keep if col not in df.columns]
    if len(missing_cols) > 0:
        raise ValueError(f"The dataframe is missing these columns: {missing_cols}")
        
    return df[columns_to_keep].copy()

def gen_binary_categories(df, tags_to_check):
    """
    Creates new True/False columns for specific genres.
    Example: If tags_to_check is ['Shounen'], it creates a column 'is_shounen'.
    """
    if 'genres' not in df.columns:
        raise ValueError("Cannot find 'genres' column in the dataframe.")
        
    df_out = df.copy()
    for tag in tags_to_check:
        clean_tag_name = tag.lower().replace(' ', '_')
        new_col_name = BINARY_CATEGORY_PREFIX + clean_tag_name

        # not case sensitive, if genres is missing, set to False
        df_out[new_col_name] = df_out['genres'].str.contains(tag, case=False, na=False)

    return df_out

def filter_multicategory_anime(df, tags_to_check):
    """
    Removes anime that belong to more than one of the specified categories.
    
    Example: 
    If tags_to_check is ['Shounen', 'Slice of Life'], this function removes anime 
    that are both Shounen and Slice of Life. It keeps anime that are just Shounen, 
    just Slice of Life, or neither.
    """
    if not tags_to_check:
        return df.copy()
        
    if 'genres' not in df.columns:
        raise ValueError("Cannot find 'genres' column in the dataframe.")
        
    clean_tags_to_check = [BINARY_CATEGORY_PREFIX+tag.lower().replace(' ', '_') for tag in tags_to_check]
    missing_cols = [tag for tag in clean_tags_to_check if tag not in df.columns]
    if len(missing_cols) > 0:
        raise ValueError(f"The dataframe is missing these columns: {missing_cols}")

    matches_count = df[clean_tags_to_check].sum(axis=1)
    df_out = df[matches_count <= 1].copy()
    return df_out


# sample function
def add(a, b):
    return a+b
