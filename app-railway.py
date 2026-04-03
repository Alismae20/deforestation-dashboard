"""
Production-ready Flask application for Railway deployment
Handles file upload, model training, predictions, and visualizations.
"""

import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
from datetime import datetime

# Import configuration and utilities
from config import (
    DEBUG, SECRET_KEY, UPLOAD_FOLDER, ALLOWED_EXTENSIONS,
    LSTM_TRAINING_START, LSTM_TRAINING_END
)
from utils.data_handler import (
    allowed_file, validate_csv, preprocess_data, 
    get_loss_columns, get_data_summary
)
from models.random_forest import RandomForestModel
from models.lstm_model import LSTMRegressionModel, LSTMClassificationModel

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
CORS(app, origins=["*"])  # Allow all origins for Railway

# Global state for models and data
state = {
    'df_uploaded': None,
    'df_preprocessed': None,
    'rf_model': RandomForestModel(),
    'lstm_regression': LSTMRegressionModel(),
    'lstm_classification': LSTMClassificationModel(),
    'models_trained': False,
    'upload_timestamp': None
}


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'message': 'Deforestation Dashboard API is running'})


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Handle CSV file upload.
    Validates structure and prepares data for modeling.
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File must be CSV format'}), 400
        
        # Save file
        filename = secure_filename(f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)
        
        # Validate CSV structure
        is_valid, message, df = validate_csv(filepath)
        
        if not is_valid:
            os.remove(filepath)
            return jsonify({'error': message}), 400
        
        # Preprocess data
        try:
            df_preprocessed = preprocess_data(df)
        except Exception as e:
            os.remove(filepath)
            return jsonify({'error': f'Data preprocessing failed: {str(e)}'}), 400
        
        # Store in state
        state['df_uploaded'] = df
        state['df_preprocessed'] = df_preprocessed
        state['upload_timestamp'] = datetime.now().isoformat()
        state['models_trained'] = False
        
        # Reset models
        state['rf_model'] = RandomForestModel()
        state['lstm_regression'] = LSTMRegressionModel()
        state['lstm_classification'] = LSTMClassificationModel()
        
        # Generate summary
        summary = get_data_summary(df_preprocessed)
        
        return jsonify({
            'success': True,
            'message': 'File uploaded and validated successfully',
            'filename': filename,
            'summary': summary
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@app.route('/api/models/train', methods=['POST'])
def train_models():
    """
    Train both Random Forest and LSTM models.
    """
    try:
        if state['df_preprocessed'] is None:
            return jsonify({'error': 'No data uploaded. Please upload a CSV file first.'}), 400
        
        df = state['df_preprocessed']
        
        # Train Random Forest
        print("Training Random Forest...")
        rf_metrics = state['rf_model'].train(df)
        
        # Train LSTM Regression
        print("Training LSTM Regression...")
        lstm_reg_metrics = state['lstm_regression'].train(df)
        
        # Train LSTM Classification
        print("Training LSTM Classification...")
        lstm_clf_metrics = state['lstm_classification'].train(df)
        
        state['models_trained'] = True
        
        return jsonify({
            'success': True,
            'message': 'All models trained successfully',
            'random_forest': rf_metrics,
            'lstm_regression': lstm_reg_metrics,
            'lstm_classification': lstm_clf_metrics
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Model training failed: {str(e)}'}), 500


@app.route('/api/visualizations/loss-trend', methods=['GET'])
def get_loss_trend():
    """
    Get loss per year data for line chart visualization.
    """
    try:
        if state['df_uploaded'] is None:
            return jsonify({'error': 'No data available'}), 400
        
        loss_cols = get_loss_columns()
        years = list(range(2001, 2025))
        
        # Sum loss across all municipalities per year
        loss_per_year = state['df_uploaded'][loss_cols].sum()
        
        return jsonify({
            'years': years,
            'loss_values': [float(x) for x in loss_per_year.values],
            'total_loss': float(loss_per_year.sum())
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/visualizations/top-municipalities', methods=['GET'])
def get_top_municipalities():
    """
    Get top 10 municipalities by cumulative loss.
    """
    try:
        if state['df_preprocessed'] is None:
            return jsonify({'error': 'No data available'}), 400
        
        df = state['df_preprocessed']
        top_10 = df.nlargest(10, 'loss_total_2001_2024')[
            ['subnational1', 'subnational2', 'loss_total_2001_2024', 'loss_rate']
        ].copy()
        
        top_10['label'] = top_10['subnational2'] + ' (' + top_10['subnational1'] + ')'
        
        return jsonify({
            'municipalities': top_10['label'].tolist(),
            'loss_values': [float(x) for x in top_10['loss_total_2001_2024'].values],
            'loss_rates': [float(x) for x in top_10['loss_rate'].values]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/predictions/random-forest', methods=['GET'])
def get_rf_predictions():
    """
    Get Random Forest predictions for all municipalities.
    """
    try:
        if not state['models_trained']:
            return jsonify({'error': 'Models not trained yet. Please train models first.'}), 400
        
        df = state['df_preprocessed']
        rf_preds, rf_probs = state['rf_model'].predict_all(df)
        
        results = df[['country', 'subnational1', 'subnational2', 'tc_loss_ha_2023', 'loss_threshold']].copy()
        results['predicted_risk'] = rf_preds
        results['predicted_probability'] = rf_probs
        results['risk_label'] = results['predicted_risk'].map({0: 'Low Risk', 1: 'High Risk'})
        
        return jsonify({
            'predictions': results.to_dict('records'),
            'metrics': state['rf_model'].metrics,
            'confusion_matrix': state['rf_model'].confusion_matrix
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/predictions/lstm-regression', methods=['GET'])
def get_lstm_regression_predictions():
    """
    Get LSTM regression predictions (actual loss values).
    """
    try:
        if not state['models_trained']:
            return jsonify({'error': 'Models not trained yet. Please train models first.'}), 400
        
        df = state['df_preprocessed']
        lstm_preds = state['lstm_regression'].predict_all(df)
        
        results = df[['country', 'subnational1', 'subnational2', 'tc_loss_ha_2023']].copy()
        results['predicted_loss_2023_ha'] = lstm_preds
        results['prediction_error'] = np.abs(results['tc_loss_ha_2023'] - results['predicted_loss_2023_ha'])
        
        return jsonify({
            'predictions': results.to_dict('records'),
            'metrics': state['lstm_regression'].metrics,
            'training_history': state['lstm_regression'].get_training_history()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/predictions/lstm-classification', methods=['GET'])
def get_lstm_classification_predictions():
    """
    Get LSTM classification predictions (high vs low risk).
    """
    try:
        if not state['models_trained']:
            return jsonify({'error': 'Models not trained yet. Please train models first.'}), 400
        
        df = state['df_preprocessed']
        lstm_probs = state['lstm_classification'].predict_all(df)
        
        results = df[['country', 'subnational1', 'subnational2', 'tc_loss_ha_2023', 'y_target']].copy()
        results['high_loss_probability'] = lstm_probs
        results['predicted_class'] = (lstm_probs >= 0.5).astype(int)
        results['predicted_label'] = results['predicted_class'].map({0: 'Low Risk', 1: 'High Risk'})
        results['actual_label'] = results['y_target'].map({0: 'Low Risk', 1: 'High Risk'})
        
        return jsonify({
            'predictions': results.to_dict('records'),
            'metrics': state['lstm_classification'].metrics,
            'training_history': state['lstm_classification'].get_training_history()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/predictions', methods=['GET'])
def export_predictions():
    """
    Export all predictions as JSON.
    """
    try:
        if not state['models_trained']:
            return jsonify({'error': 'Models not trained yet.'}), 400
        
        df = state['df_preprocessed']
        
        # Get all predictions
        rf_preds, rf_probs = state['rf_model'].predict_all(df)
        lstm_reg_preds = state['lstm_regression'].predict_all(df)
        lstm_clf_probs = state['lstm_classification'].predict_all(df)
        
        results = df[['country', 'subnational1', 'subnational2', 'tc_loss_ha_2023']].copy()
        results['rf_predicted_class'] = rf_preds
        results['rf_probability'] = rf_probs
        results['lstm_predicted_loss_ha'] = lstm_reg_preds
        results['lstm_high_loss_probability'] = lstm_clf_probs
        
        # Convert to list of records
        export_data = results.to_dict('records')
        
        return jsonify({
            'success': True,
            'data': export_data,
            'timestamp': state['upload_timestamp'],
            'total_records': len(export_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/data-summary', methods=['GET'])
def data_summary():
    """Get overall data summary."""
    try:
        if state['df_preprocessed'] is None:
            return jsonify({'error': 'No data available'}), 400
        
        summary = get_data_summary(state['df_preprocessed'])
        summary['models_trained'] = state['models_trained']
        
        return jsonify(summary), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Create upload folder if not exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Get port from environment variable (Railway)
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting Deforestation Dashboard API on port {port}...")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    
    # Production: use gunicorn (via Procfile)
    # Development: use Flask development server
    if os.environ.get('FLASK_ENV') == 'production':
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        app.run(debug=DEBUG, host='0.0.0.0', port=port)
