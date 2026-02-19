import pandas as pd
import numpy as np


# CONFIGS
USEFUL_COLS = ['anime_id', 'title', 'type', 'episodes', 
               'duration', 'genres', 'start_date', 'end_date',
               'status']
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

def add_airing_date_features(df: pd.DataFrame, ref_date="2026-02-01") -> pd.DataFrame:
    # Adds start_year, end_year, aired_days.
    # For status == 'currently_airing', aired_days is computed up to ref_date (inclusive).
    out = df.copy()

    out["start_date"] = pd.to_datetime(out["start_date"], errors="coerce")
    out["end_date"]   = pd.to_datetime(out["end_date"],   errors="coerce")

    out["start_year"] = out["start_date"].dt.year
    out["end_year"]   = out["end_date"].dt.year

    bad_range = out["start_date"].notna() & out["end_date"].notna() & (out["end_date"] < out["start_date"])
    out.loc[bad_range, ["start_date", "end_date"]] = pd.NaT
    out.loc[bad_range, ["start_year", "end_year"]] = np.nan

    out["aired_days"] = np.where(
        out["start_date"].notna() & out["end_date"].notna(),
        (out["end_date"] - out["start_date"]).dt.days + 1,
        np.nan
    )

    ref_ts = pd.Timestamp(ref_date)
    mask_curr = (out["status"] == "currently_airing") & out["start_date"].notna()
    days_to_ref = (ref_ts - out.loc[mask_curr, "start_date"]).dt.days + 1
    out.loc[mask_curr, "aired_days"] = days_to_ref.clip(lower=1)
    out.loc[mask_curr, "end_year"] = ref_ts.year  # optional but usually convenient

    return out

def seconds_to_mins(df, duration_column):
    # Given duration column containing int representing seconds, convert from seconds to min rounded to integer
    df[duration_column] = (df[duration_column] / 60).round().astype(int)
    return df
