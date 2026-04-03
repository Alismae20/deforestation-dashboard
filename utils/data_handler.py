"""
Data handling utilities for CSV upload, validation, and preprocessing.
"""

import pandas as pd
import numpy as np
from werkzeug.utils import secure_filename
import os
from config import ALLOWED_EXTENSIONS, THRESHOLD_VALUE, LSTM_TRAINING_START, LSTM_TRAINING_END


def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_csv(filepath):
    """
    Validate CSV file structure and required columns.
    Returns tuple: (is_valid, message, dataframe)
    """
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        return False, f"Error reading CSV file: {str(e)}", None

    # Check required columns
    required_cols = ['country', 'subnational1', 'subnational2', 'threshold', 'area_ha', 
                     'extent_2000_ha', 'extent_2010_ha', 'gain_2000-2012_ha']
    
    for col in required_cols:
        if col not in df.columns:
            return False, f"Missing required column: '{col}'", None
    
    # Check for loss columns (2001-2024)
    loss_cols = [f'tc_loss_ha_{year}' for year in range(2001, 2025)]
    missing_loss_cols = [col for col in loss_cols if col not in df.columns]
    
    if missing_loss_cols:
        return False, f"Missing loss columns: {', '.join(missing_loss_cols[:3])}...", None
    
    # Check for duplicates and basic data quality
    if df.isnull().sum().sum() > 0:
        # Fill NaN with 0 for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)
    
    return True, "CSV validation successful", df


def preprocess_data(df):
    """
    Preprocess data: filter by threshold, create features.
    Returns preprocessed dataframe.
    """
    # Filter by threshold
    df_filtered = df[df['threshold'] == THRESHOLD_VALUE].copy()
    
    if len(df_filtered) == 0:
        raise ValueError(f"No data found with threshold={THRESHOLD_VALUE}")
    
    # Ensure numeric columns
    loss_cols = [f'tc_loss_ha_{year}' for year in range(2001, 2025)]
    for col in loss_cols + ['extent_2000_ha', 'extent_2010_ha', 'gain_2000-2012_ha', 'area_ha']:
        if col in df_filtered.columns:
            df_filtered[col] = pd.to_numeric(df_filtered[col], errors='coerce').fillna(0)
    
    # Create target for classification: high vs low deforestation in 2023
    threshold_high = df_filtered['tc_loss_ha_2023'].quantile(0.75)
    df_filtered['y_target'] = (df_filtered['tc_loss_ha_2023'] >= threshold_high).astype(int)
    df_filtered['loss_threshold'] = threshold_high
    
    # Create feature columns for Random Forest (using 2015-2022, no data leakage)
    feature_cols = ['extent_2000_ha', 'extent_2010_ha', 'gain_2000-2012_ha'] + \
                   [f'tc_loss_ha_{year}' for year in range(LSTM_TRAINING_START, LSTM_TRAINING_END + 1)]
    
    df_filtered['feature_cols'] = ','.join(feature_cols)
    
    # Create time-series columns for LSTM (2015-2022)
    lstm_cols = [f'tc_loss_ha_{year}' for year in range(LSTM_TRAINING_START, LSTM_TRAINING_END + 1)]
    df_filtered['timeseries_cols'] = ','.join(lstm_cols)
    
    # Compute cumulative loss for visualizations
    all_loss_cols = [f'tc_loss_ha_{year}' for year in range(2001, 2025)]
    df_filtered['loss_total_2001_2024'] = df_filtered[all_loss_cols].sum(axis=1)
    df_filtered['loss_total_2001_2023'] = df_filtered[[col for col in all_loss_cols if col != 'tc_loss_ha_2024']].sum(axis=1)
    df_filtered['loss_rate'] = df_filtered['loss_total_2001_2024'] / (df_filtered['extent_2000_ha'] + 1)
    
    return df_filtered


def get_loss_columns(start_year=2001, end_year=2024):
    """Get list of loss column names for a year range."""
    return [f'tc_loss_ha_{year}' for year in range(start_year, end_year + 1)]


def get_data_summary(df_filtered):
    """Generate summary statistics for the dataset."""
    loss_cols = get_loss_columns()
    
    return {
        'total_rows': len(df_filtered),
        'unique_provinces': len(df_filtered['subnational1'].unique()),
        'unique_municipalities': len(df_filtered['subnational2'].unique()),
        'provinces': sorted(df_filtered['subnational1'].unique().tolist()),
        'total_loss_2001_2024': float(df_filtered['loss_total_2001_2024'].sum()),
        'total_loss_2023': float(df_filtered['tc_loss_ha_2023'].sum()),
        'avg_loss_per_municipality_2023': float(df_filtered['tc_loss_ha_2023'].mean()),
        'max_loss_municipality': df_filtered.loc[df_filtered['loss_total_2001_2024'].idxmax(), 'subnational2'],
        'max_loss_value': float(df_filtered['loss_total_2001_2024'].max()),
    }
