"""
Configuration settings for the deforestation dashboard backend.
"""

import os
from datetime import timedelta

# Flask Configuration
DEBUG = True
SECRET_KEY = 'deforestation-dashboard-secret-key-2024'

# Upload Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../uploads')
ALLOWED_EXTENSIONS = {'csv'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB max file size

# ML Model Configuration
THRESHOLD_VALUE = 30  # Filter data to threshold=30
TEST_SIZE = 0.2
RANDOM_STATE = 42
STRATIFY = True

# LSTM Configuration
LSTM_TIMESTEPS = 8  # 2015-2022 (8 years)
LSTM_EPOCHS = 100
LSTM_BATCH_SIZE = 32
LSTM_VALIDATION_SPLIT = 0.2
LSTM_EARLY_STOPPING_PATIENCE = 10

# Random Forest Configuration
RF_N_ESTIMATORS = 100
RF_MAX_DEPTH = 10

# Classification threshold
HIGH_LOSS_PERCENTILE = 0.75  # Top 25%

# Year configuration
HISTORICAL_START_YEAR = 2001
LSTM_TRAINING_START = 2015
LSTM_TRAINING_END = 2022
TARGET_YEAR = 2023

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
