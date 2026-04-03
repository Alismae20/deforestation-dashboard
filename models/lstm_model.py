"""
LSTM Deep Learning Model for Time-Series Deforestation Prediction.
Predicts 2023 tree cover loss and high vs low classification.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    confusion_matrix, accuracy_score, f1_score
)
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

from config import (
    LSTM_TIMESTEPS, LSTM_EPOCHS, LSTM_BATCH_SIZE,
    LSTM_VALIDATION_SPLIT, LSTM_EARLY_STOPPING_PATIENCE,
    LSTM_TRAINING_START, LSTM_TRAINING_END, RANDOM_STATE, TEST_SIZE
)


class LSTMRegressionModel:
    """LSTM model for regression (predict 2023 loss in hectares)."""
    
    def __init__(self):
        self.model = None
        self.scaler = MinMaxScaler()
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.history = None
        self.metrics = None
        self.y_pred = None
        
    def prepare_data(self, df_filtered):
        """
        Prepare time-series data for LSTM.
        Uses 2015-2022 as input, 2023 as target.
        """
        years = list(range(LSTM_TRAINING_START, LSTM_TRAINING_END + 1))
        loss_cols = [f'tc_loss_ha_{year}' for year in years]
        
        # Extract time-series (municipalities x years)
        X_timeseries = df_filtered[loss_cols].values.astype(np.float32)
        y_regression = df_filtered['tc_loss_ha_2023'].values.astype(np.float32)
        
        # Normalize time-series
        X_flat = X_timeseries.reshape(-1, 1)
        X_scaled = self.scaler.fit_transform(X_flat).reshape(X_timeseries.shape)
        
        # Reshape for LSTM (samples, timesteps, features)
        X_reshaped = X_scaled.reshape((X_scaled.shape[0], X_scaled.shape[1], 1))
        
        return X_reshaped, y_regression
    
    def train(self, df_filtered):
        """Train the LSTM regression model."""
        X, y = self.prepare_data(df_filtered)
        
        # Split data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
        )
        
        # Build model (small to prevent overfitting)
        self.model = Sequential([
            LSTM(32, activation='relu', input_shape=(LSTM_TIMESTEPS, 1), return_sequences=True),
            Dropout(0.3),
            LSTM(16, activation='relu'),
            Dropout(0.3),
            Dense(8, activation='relu'),
            Dense(1)
        ])
        
        self.model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
        
        # Early stopping
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=LSTM_EARLY_STOPPING_PATIENCE,
            restore_best_weights=True,
            verbose=0
        )
        
        # Train
        self.history = self.model.fit(
            self.X_train, self.y_train,
            epochs=LSTM_EPOCHS,
            batch_size=LSTM_BATCH_SIZE,
            validation_split=LSTM_VALIDATION_SPLIT,
            callbacks=[early_stop],
            verbose=0
        )
        
        # Evaluate
        self._evaluate()
        
        return self.metrics
    
    def _evaluate(self):
        """Evaluate regression model."""
        self.y_pred = self.model.predict(self.X_test, verbose=0).flatten()
        
        mse = mean_squared_error(self.y_test, self.y_pred)
        mae = mean_absolute_error(self.y_test, self.y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(self.y_test, self.y_pred)
        
        # Overfitting check
        final_train_loss = self.history.history['loss'][-1]
        final_val_loss = self.history.history['val_loss'][-1]
        overfitting_gap = final_val_loss - final_train_loss
        
        self.metrics = {
            'mae': float(mae),
            'rmse': float(rmse),
            'r2_score': float(r2),
            'mse': float(mse),
            'epochs_trained': len(self.history.history['loss']),
            'overfitting_gap': float(overfitting_gap),
            'test_size': len(self.X_test),
            'train_size': len(self.X_train),
            'final_train_loss': float(final_train_loss),
            'final_val_loss': float(final_val_loss)
        }
    
    def predict(self, X):
        """Make predictions."""
        if self.model is None:
            raise ValueError("Model not trained yet")
        return self.model.predict(X, verbose=0).flatten()
    
    def predict_all(self, df_filtered):
        """Predict for all data."""
        X, _ = self.prepare_data(df_filtered)
        X_reshaped = X.reshape((X.shape[0], LSTM_TIMESTEPS, 1))
        return self.predict(X_reshaped)
    
    def get_training_history(self):
        """Get training history for plotting."""
        if self.history is None:
            return None
        
        return {
            'loss': [float(x) for x in self.history.history['loss']],
            'val_loss': [float(x) for x in self.history.history['val_loss']],
            'mae': [float(x) for x in self.history.history['mae']],
            'val_mae': [float(x) for x in self.history.history['val_mae']]
        }


class LSTMClassificationModel:
    """LSTM model for classification (high vs low deforestation)."""
    
    def __init__(self):
        self.model = None
        self.scaler = MinMaxScaler()
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.history = None
        self.metrics = None
        self.y_pred_proba = None
        
    def prepare_data(self, df_filtered):
        """Prepare time-series data and classification target."""
        years = list(range(LSTM_TRAINING_START, LSTM_TRAINING_END + 1))
        loss_cols = [f'tc_loss_ha_{year}' for year in years]
        
        # Extract time-series
        X_timeseries = df_filtered[loss_cols].values.astype(np.float32)
        
        # Target: 2023 high vs low
        y_classification = df_filtered['y_target'].values.astype(np.float32)
        
        # Normalize
        X_flat = X_timeseries.reshape(-1, 1)
        X_scaled = self.scaler.fit_transform(X_flat).reshape(X_timeseries.shape)
        
        # Reshape for LSTM
        X_reshaped = X_scaled.reshape((X_scaled.shape[0], X_scaled.shape[1], 1))
        
        return X_reshaped, y_classification
    
    def train(self, df_filtered):
        """Train LSTM classification model."""
        X, y = self.prepare_data(df_filtered)
        
        # Split data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=(y > 0.5).astype(int)
        )
        
        # Build model
        self.model = Sequential([
            LSTM(32, activation='relu', input_shape=(LSTM_TIMESTEPS, 1), return_sequences=True),
            Dropout(0.3),
            LSTM(16, activation='relu'),
            Dropout(0.3),
            Dense(8, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        # Early stopping
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=LSTM_EARLY_STOPPING_PATIENCE,
            restore_best_weights=True,
            verbose=0
        )
        
        # Train
        self.history = self.model.fit(
            self.X_train, self.y_train,
            epochs=LSTM_EPOCHS,
            batch_size=LSTM_BATCH_SIZE,
            validation_split=LSTM_VALIDATION_SPLIT,
            callbacks=[early_stop],
            verbose=0
        )
        
        # Evaluate
        self._evaluate()
        
        return self.metrics
    
    def _evaluate(self):
        """Evaluate classification model."""
        self.y_pred_proba = self.model.predict(self.X_test, verbose=0).flatten()
        y_pred = (self.y_pred_proba >= 0.5).astype(int)
        
        accuracy = accuracy_score(self.y_test, y_pred)
        f1 = f1_score(self.y_test, y_pred, zero_division=0)
        cm = confusion_matrix(self.y_test, y_pred).tolist()
        
        # Overfitting check
        final_train_acc = self.history.history['accuracy'][-1]
        final_val_acc = self.history.history['val_accuracy'][-1]
        overfitting_gap = final_train_acc - final_val_acc
        
        self.metrics = {
            'accuracy': float(accuracy),
            'f1_score': float(f1),
            'epochs_trained': len(self.history.history['accuracy']),
            'overfitting_gap': float(overfitting_gap),
            'confusion_matrix': cm,
            'test_size': len(self.X_test),
            'train_size': len(self.X_train),
            'final_train_accuracy': float(final_train_acc),
            'final_val_accuracy': float(final_val_acc)
        }
    
    def predict(self, X):
        """Make probability predictions."""
        if self.model is None:
            raise ValueError("Model not trained yet")
        return self.model.predict(X, verbose=0).flatten()
    
    def predict_all(self, df_filtered):
        """Predict for all data."""
        X, _ = self.prepare_data(df_filtered)
        X_reshaped = X.reshape((X.shape[0], LSTM_TIMESTEPS, 1))
        return self.predict(X_reshaped)
    
    def get_training_history(self):
        """Get training history for plotting."""
        if self.history is None:
            return None
        
        return {
            'accuracy': [float(x) for x in self.history.history['accuracy']],
            'val_accuracy': [float(x) for x in self.history.history['val_accuracy']],
            'loss': [float(x) for x in self.history.history['loss']],
            'val_loss': [float(x) for x in self.history.history['val_loss']]
        }
