# Machine Learning Models Documentation

## Overview

The deforestation detection system uses three complementary models:

1. **Random Forest** - Interpretable classification
2. **LSTM Regression** - Time-series loss prediction
3. **LSTM Classification** - Deep learning risk prediction

Each model targets different aspects of forest loss prediction.

## 1. Random Forest Classifier

### Purpose
Binary classification of 2023 forest loss as "High Risk" or "Low Risk"

### Data & Features

**Training Data:**
- Years: 2015-2022 (8 years)
- Features extracted: 11 total

**Feature Set:**
```
1. loss_2015, loss_2016, ..., loss_2022  (8 loss columns)
2. extent_loss_pct_2015_2022             (aggregate metric)
3. loss_rate (hectares/year)             (trend indicator)
```

**Target Variable:**
- 2023 forest loss (hectares)
- Binary: 0=Low Risk (<30 ha), 1=High Risk (≥30 ha)

**Data Leakage Prevention:**
✅ Uses only 2015-2022 (training years)
✅ 2023 target NOT included in features
✅ No future data leak

### Model Architecture

```python
RandomForestClassifier(
    n_estimators=100,      # 100 decision trees
    max_depth=10,          # Tree depth limit (prevents overfitting)
    min_samples_split=5,   # Min samples to split node
    random_state=42        # Reproducibility
)
```

**Why Random Forest?**
- Fast training (30-40 seconds)
- Interpretable (feature importance)
- Good accuracy (75-90%)
- Robust to outliers
- No scaling required

### Training Process

```python
# Pseudocode
1. Load preprocessed data
2. Extract features from 2015-2022 data
3. Get 2023 target (high/low classification)
4. Split: 80% train, 20% test
5. Train: RF.fit(X_train, y_train)
6. Evaluate: metrics on X_test, y_test
```

### Output

For each municipality:
```json
{
    "municipality": "Amazon-Municipality1",
    "predicted_class": 1,           // 0=Low, 1=High
    "predicted_probability": 0.87,  // Confidence 0-1
    "risk_label": "High Risk"
}
```

### Evaluation Metrics

```
Accuracy:  TP+TN / Total          (overall correctness)
Precision: TP / (TP+FP)           (false positive rate)
Recall:    TP / (TP+FN)           (false negative rate)
F1-Score:  2*(Precision*Recall)   (harmonic mean)
Confusion Matrix:
    [[TN  FP]
     [FN  TP]]
```

**Typical Performance:**
- Accuracy: 80-85%
- Precision: 0.75-0.90
- Recall: 0.70-0.85
- F1-Score: 0.75-0.85

### Feature Importance

Example (from trained model):
```
loss_2022:        0.25  (most recent year)
loss_2021:        0.18
loss_2020:        0.15
loss_rate:        0.12
extent_pct:       0.10
loss_2019-2015:   0.20  (historical)
```

Higher values = more predictive power

## 2. LSTM Regression Model

### Purpose
Predict actual 2023 forest loss value (continuous, in hectares)

### Data & Features

**Training Data:**
- Years: 2015-2022 (8-year sequence)
- Normalized with MinMaxScaler (0-1 range)

**Feature Processing:**
```
Raw: [10, 12, 8, 15, 20, 18, 22, 25]  (2015-2022)
Normalize: [0.0, 0.12, 0.08, 0.15, 0.20, 0.18, 0.22, 0.25]
Shape: (n_samples, 8_timesteps, 1_feature)
```

**Target Variable:**
- 2023 forest loss (continuous value)
- Example: 28.5 hectares

### Model Architecture

```python
Sequential([
    LSTM(32, activation='relu', 
         input_shape=(8, 1),         # 8 timesteps, 1 feature
         return_sequences=True),
    Dropout(0.3),                    # 30% dropout
    
    LSTM(16, activation='relu'),
    Dropout(0.3),
    
    Dense(8, activation='relu'),
    Dense(1)                         # Output: single value
])
```

**Architecture Explanation:**
```
Input: [B, 8, 1]           (batch, timesteps, features)
    ↓
LSTM(32): [B, 8, 32]       (processes sequence, returns all steps)
    ↓
Dropout: randomly disable 30% of units
    ↓
LSTM(16): [B, 16]          (returns only last step)
    ↓
Dropout: randomly disable 30% of units
    ↓
Dense(8): [B, 8]           (fully connected)
    ↓
Dense(1): [B, 1]           (single output value)
```

**Why LSTM?**
- Learns temporal patterns (trends)
- Captures long-term dependencies
- Better than dense networks for sequences
- Early stopping prevents overfitting

### Training Process

```
Hyperparameters:
- Epochs: 100
- Batch size: 32
- Learning rate: default Adam (0.001)
- Loss function: Mean Squared Error (MSE)
- Early Stopping: patience=10, monitor='val_loss'

Process:
1. Normalize all 8-year sequences
2. Reshape to LSTM format
3. Split: 80% train, 20% validation
4. Train: model.fit() with early stopping
5. Evaluate on test data
```

**Early Stopping Logic:**
```
If validation_loss doesn't improve for 10 epochs → stop training
Example:
Epoch 1: val_loss=50.2
Epoch 2: val_loss=48.5  ✓ (improved)
Epoch 3: val_loss=47.8  ✓ (improved)
...
Epoch 13: val_loss=45.1 (no improvement for 10 epochs)
          → STOP training (prevents overfitting)
```

### Output

For each municipality:
```json
{
    "municipality": "Amazon-Municipality1",
    "actual_loss_2023_ha": 28.5,
    "predicted_loss_2023_ha": 26.3,
    "prediction_error": 2.2           // |actual - predicted|
}
```

### Evaluation Metrics

```
MAE (Mean Absolute Error):
  Average of |y_true - y_pred|
  Example: 4.5 ha (on average off by 4.5 ha)

RMSE (Root Mean Squared Error):
  √(average of (y_true - y_pred)²)
  Example: 6.2 ha (penalizes large errors more)

R² Score (Coefficient of Determination):
  1 - (residual_sum_sq / total_sum_sq)
  Range: 0-1 (higher is better)
  0.7 = 70% of variance explained

Overfitting Gap:
  |train_loss - val_loss| / val_loss
  > 0.5 = significant overfitting
  < 0.2 = good fit
```

**Typical Performance:**
- MAE: 3.0-5.0 ha
- RMSE: 4.5-7.0 ha
- R²: 0.65-0.80
- Overfitting Gap: 0.1-0.3

## 3. LSTM Classification Model

### Purpose
Predict high/low risk probability (0-1 scale) using deep learning

### Data & Features

**Identical to LSTM Regression:**
- Years: 2015-2022 normalized sequence
- Target: binary (high/low risk)

### Model Architecture

```python
Sequential([
    LSTM(32, activation='relu',
         input_shape=(8, 1),
         return_sequences=True),
    Dropout(0.3),
    
    LSTM(16, activation='relu'),
    Dropout(0.3),
    
    Dense(8, activation='relu'),
    Dense(1, activation='sigmoid')  # Probability output
])
```

**Key Difference from Regression:**
- Output layer: `sigmoid` activation (0-1)
- Loss: `binary_crossentropy` (classification)
- Metric: `accuracy` (vs MAE for regression)

**Sigmoid Function:**
```
sigmoid(x) = 1 / (1 + e^-x)

Example outputs:
  x = -2  → sigmoid = 0.12  (12% probability)
  x = 0   → sigmoid = 0.50  (50% probability)
  x = 2   → sigmoid = 0.88  (88% probability)
```

### Training Process

```
Configuration:
- Epochs: 100
- Batch size: 32
- Loss function: Binary Crossentropy
- Optimizer: Adam
- Early Stopping: patience=10

Binary Crossentropy Loss:
  - Penalizes confident wrong predictions
  - Better than MSE for classification
  - Encourages probabilities close to 0 or 1
```

### Output

For each municipality:
```json
{
    "municipality": "Amazon-Municipality1",
    "high_loss_probability": 0.85,   // 85% chance of high risk
    "predicted_class": 1,            // 0=Low, 1=High
    "predicted_label": "High Risk",
    "actual_label": "High Risk"
}
```

**Decision Rule:**
```
probability >= 0.5 → predict "High Risk" (class 1)
probability < 0.5  → predict "Low Risk" (class 0)
```

### Evaluation Metrics

**Same as Random Forest:**
- Accuracy: % correct predictions
- Precision: TP / (TP+FP)
- Recall: TP / (TP+FN)
- F1-Score: harmonic mean

**Typical Performance:**
- Accuracy: 75-85%
- Precision: 0.70-0.85
- Recall: 0.75-0.90
- F1-Score: 0.72-0.87

## Model Comparison

| Aspect | Random Forest | LSTM Reg | LSTM Clf |
|--------|---------------|----------|----------|
| **Task** | Classification | Regression | Classification |
| **Output** | 0/1 + prob | Continuous | 0-1 probability |
| **Training** | 30-40 sec | 2-5 min | 2-5 min |
| **Accuracy** | 75-90% | RMSE 4-7 | 75-85% |
| **Interpretable** | High (features) | Low | Low |
| **Temporal** | No (aggregate) | Yes (sequence) | Yes (sequence) |
| **Overfitting** | Low | Medium | Medium |
| **Best for** | Quick, interpretable | Trends | Deep patterns |

## Anti-Overfitting Strategies

### 1. Data Leakage Prevention
```python
✅ Use 2015-2022 ONLY for features
✅ Predict 2023 (unseen target)
❌ Never include 2023 in features
```

### 2. Regularization
```python
# Dropout: randomly disable units
Dropout(0.3)  # Disable 30% each epoch

# Early Stopping: stop if no improvement
EarlyStopping(patience=10)

# Limited depth (RF)
max_depth=10
```

### 3. Train/Test Split
```python
80% train   (learn patterns)
20% test    (evaluate unseen data)
```

### 4. Validation Monitoring
```python
# For LSTM
80% train
20% validation (for early stopping)
Separate test set for final evaluation
```

## Choosing the Right Model

**Use Random Forest when:**
- Need interpretability (why predictions?)
- Want fast training
- Have limited computational power
- Features are interpretable

**Use LSTM Regression when:**
- Need continuous predictions
- Temporal trends matter
- Have time-series data
- Accuracy more important than speed

**Use LSTM Classification when:**
- Need probability estimates
- Want deep learning benefits
- Have complex patterns
- Uncertainty quantification needed

## Hyperparameter Tuning

### Random Forest
```python
config.py:
RF_ESTIMATORS = 100    # More = more accuracy, slower
RF_MAX_DEPTH = 10      # Deeper = more overfit risk
```

### LSTM
```python
config.py:
LSTM_EPOCHS = 100              # More = better, slower
LSTM_BATCH_SIZE = 32           # Smaller = more memory
LSTM_EARLY_STOPPING_PATIENCE=10 # Larger = longer training
```

## Model Persistence

### Saving Models (if implemented)
```python
# After training
import joblib

joblib.dump(rf_model, 'rf_model.pkl')
rf_model_loaded = joblib.load('rf_model.pkl')

# LSTM
model.save('lstm_model.h5')
model = keras.models.load_model('lstm_model.h5')
```

## Future Improvements

1. Ensemble: Combine all 3 models with weighted voting
2. Stacking: Use model outputs as features for meta-learner
3. Hyperparameter optimization: Grid search or Bayesian
4. Cross-validation: k-fold for more robust evaluation
5. Class balancing: Handle imbalanced high/low risk split
6. Transfer learning: Pre-train on similar domains
7. Attention mechanisms: Weight important timesteps more
