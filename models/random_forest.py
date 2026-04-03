"""
Random Forest Classification Model for Deforestation Risk Prediction.
Predicts high vs low deforestation in 2023 using 2015-2022 history.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    confusion_matrix, accuracy_score, precision_score, 
    recall_score, f1_score
)
from config import (
    LSTM_TRAINING_START, LSTM_TRAINING_END, RF_N_ESTIMATORS, 
    RF_MAX_DEPTH, RANDOM_STATE, TEST_SIZE
)


class RandomForestModel:
    """Random Forest classifier for deforestation risk."""
    
    def __init__(self):
        self.model = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.feature_cols = None
        self.feature_importance_df = None
        self.metrics = None
        self.confusion_matrix = None
        
    def prepare_features(self, df_filtered):
        """
        Prepare features for training.
        Uses 2015-2022 data (no data leakage from 2023 target).
        """
        # Feature columns: forest extent + loss 2015-2022
        self.feature_cols = [
            'extent_2000_ha', 
            'extent_2010_ha', 
            'gain_2000-2012_ha'
        ] + [f'tc_loss_ha_{year}' for year in range(LSTM_TRAINING_START, LSTM_TRAINING_END + 1)]
        
        X = df_filtered[self.feature_cols].fillna(0)
        y = df_filtered['y_target']
        
        return X, y
    
    def train(self, df_filtered):
        """Train the Random Forest model."""
        X, y = self.prepare_features(df_filtered)
        
        # Split data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
        )
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=RF_N_ESTIMATORS,
            max_depth=RF_MAX_DEPTH,
            random_state=RANDOM_STATE,
            n_jobs=-1
        )
        self.model.fit(self.X_train, self.y_train)
        
        # Evaluate
        self._evaluate()
        
        return self.metrics
    
    def _evaluate(self):
        """Evaluate model on test set."""
        y_pred = self.model.predict(self.X_test)
        y_pred_proba = self.model.predict_proba(self.X_test)[:, 1]
        
        accuracy = accuracy_score(self.y_test, y_pred)
        precision = precision_score(self.y_test, y_pred, zero_division=0)
        recall = recall_score(self.y_test, y_pred, zero_division=0)
        f1 = f1_score(self.y_test, y_pred, zero_division=0)
        
        self.confusion_matrix = confusion_matrix(self.y_test, y_pred).tolist()
        
        # Feature importance
        importance_df = pd.DataFrame({
            'feature': self.feature_cols,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        self.feature_importance_df = importance_df
        
        self.metrics = {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'test_size': len(self.X_test),
            'train_size': len(self.X_train),
            'confusion_matrix': self.confusion_matrix,
            'feature_importance': importance_df.to_dict('records')
        }
    
    def predict(self, X):
        """Make predictions on new data."""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)[:, 1]
        
        return predictions, probabilities
    
    def predict_all(self, df_filtered):
        """Get predictions for all data."""
        X, _ = self.prepare_features(df_filtered)
        predictions, probabilities = self.predict(X)
        
        return predictions, probabilities
