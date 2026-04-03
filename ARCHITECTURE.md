# Architecture & Design

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    USER BROWSER                             │
│              http://localhost:8000                          │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP Requests (Axios)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           FRONTEND (Flask + JavaScript)                     │
│           Port 8000                                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  HTML/CSS/JavaScript Dashboard                        │  │
│  │  - File upload interface                              │  │
│  │  - Chart.js visualizations                            │  │
│  │  - Model training controls                            │  │
│  │  - Results tables & export                            │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │ JSON/REST API Calls
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           BACKEND API (Flask)                               │
│           Port 5000                                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Routes:                                              │  │
│  │  - POST /api/upload                                   │  │
│  │  - POST /api/models/train                             │  │
│  │  - GET /api/predictions/*                             │  │
│  │  - GET /api/visualizations/*                          │  │
│  │  - GET /api/export/predictions                        │  │
│  └───────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
          ┌──────────┼──────────┬───────────────┐
          ▼          ▼          ▼               ▼
    ┌─────────┐ ┌────────┐ ┌──────────┐ ┌─────────────┐
    │  Data   │ │ Random │ │   LSTM   │ │   Uploads   │
    │ Handler │ │ Forest │ │  Models  │ │   Folder    │
    │ (Pandas)│ │        │ │(TF/Keras)│ │  (CSV)      │
    └─────────┘ └────────┘ └──────────┘ └─────────────┘
```

## Component Architecture

### 1. Frontend Layer (`frontend/`)

**Files:**
- `app.py` - Flask development server (port 8000)
- `templates/index.html` - Single-page application
- `static/css/style.css` - Responsive dashboard styling
- `static/js/app.js` - UI logic & API integration

**Responsibilities:**
- Render interactive dashboard
- Handle file upload with drag-and-drop
- Make async API calls (Axios)
- Render Chart.js visualizations
- Display model metrics & predictions
- Export functionality

**Technology:**
- HTML5 semantic markup
- CSS3 Grid/Flexbox responsive design
- Vanilla JavaScript (no frameworks)
- Chart.js for data visualization
- Axios for HTTP requests

### 2. Backend API Layer (`backend/app.py`)

**Core Flask Application:**
- Routes for upload, training, predictions
- CORS enabled for frontend communication
- Error handling with HTTP status codes
- Global state management for models

**Key Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/upload` | POST | CSV validation & storage |
| `/api/models/train` | POST | Train all 3 models |
| `/api/data-summary` | GET | Data statistics |
| `/api/visualizations/loss-trend` | GET | Loss per year |
| `/api/visualizations/top-municipalities` | GET | Top 10 regions |
| `/api/predictions/random-forest` | GET | RF predictions |
| `/api/predictions/lstm-regression` | GET | LSTM regression |
| `/api/predictions/lstm-classification` | GET | LSTM classification |
| `/api/export/predictions` | GET | JSON export |

### 3. Data Layer (`backend/utils/`)

**`data_handler.py`:**
- CSV validation (columns, format)
- Data preprocessing & filtering
- Feature engineering
- Target variable computation
- Data summary statistics

**Key Functions:**
```python
validate_csv()          # Validates structure
preprocess_data()       # Cleans & engineers features
get_data_summary()      # Statistics for dashboard
get_loss_columns()      # Returns 2001-2024 columns
```

### 4. Model Layer (`backend/models/`)

#### Random Forest Classifier
**File:** `random_forest.py`

```python
class RandomForestModel:
    prepare_features()  # Extract 11 features from 2015-2022 data
    train()             # Fit RF classifier
    predict_all()       # Get predictions + probabilities
    _evaluate()         # Compute metrics
```

**Configuration:**
- Estimators: 100 trees
- Max depth: 10
- Random state: 42
- Train/test split: 80/20

**Anti-data-leakage design:**
- Uses only 2015-2022 data
- Predicts 2023 target (not seen during training)

#### LSTM Regression Model
**File:** `lstm_model.py` - `LSTMRegressionModel`

```python
class LSTMRegressionModel:
    prepare_data()      # Normalize 8-year sequences
    train()             # Fit LSTM network
    predict_all()       # Predict loss values
    _evaluate()         # MAE, RMSE, R²
```

**Architecture:**
```
Input (8 timesteps, 1 feature)
    ↓
LSTM(32, return_sequences=True) + Dropout(0.3)
    ↓
LSTM(16) + Dropout(0.3)
    ↓
Dense(8, relu)
    ↓
Output (1 continuous value)
```

**Training:**
- Epochs: 100
- Batch size: 32
- Loss: MSE
- Optimizer: Adam
- Early stopping: patience 10

#### LSTM Classification Model
**File:** `lstm_model.py` - `LSTMClassificationModel`

```python
class LSTMClassificationModel:
    prepare_data()      # Same normalization
    train()             # Fit classification network
    predict_all()       # Probability predictions
    _evaluate()         # Accuracy, precision, recall
```

**Architecture:**
- Same as regression but with sigmoid output
- Loss: Binary crossentropy
- Output: 0-1 probability

### 5. Configuration Layer (`backend/config.py`)

```python
# Flask
DEBUG = True
SECRET_KEY = os.urandom(24)

# Upload
UPLOAD_FOLDER = '../uploads'
MAX_FILE_SIZE = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {'csv'}

# LSTM
LSTM_EPOCHS = 100
LSTM_BATCH_SIZE = 32
LSTM_EARLY_STOPPING_PATIENCE = 10
LSTM_TIMESTEPS = 8
LSTM_TRAINING_START = 2015
LSTM_TRAINING_END = 2022

# Random Forest
RF_ESTIMATORS = 100
RF_MAX_DEPTH = 10

# Data
DATA_THRESHOLD = 30  # Filter municipalities
TARGET_LOSS_YEAR = 2023
HIGH_RISK_THRESHOLD = 30  # hectares
```

## Data Flow

### 1. Upload Phase
```
User CSV File
    ↓
Frontend: File selected/dropped
    ↓
POST /api/upload (Axios)
    ↓
Backend: receive & validate
    ↓
data_handler.validate_csv()
    ↓
data_handler.preprocess_data()
    ↓
Store in state['df_preprocessed']
    ↓
Response: summary statistics
    ↓
Frontend: display data info
```

### 2. Training Phase
```
POST /api/models/train
    ↓
Random Forest:
  - prepare_features(2015-2022 data)
  - train() → state['rf_model']
  - metrics
    ↓
LSTM Regression:
  - prepare_data(normalize)
  - train() → state['lstm_regression']
  - metrics
    ↓
LSTM Classification:
  - prepare_data(normalize)
  - train() → state['lstm_classification']
  - metrics
    ↓
Response: all metrics
    ↓
Frontend: display in cards
```

### 3. Prediction Phase
```
GET /api/predictions/random-forest
    ↓
df_preprocessed + trained rf_model
    ↓
rf_preds, rf_probs = predict_all()
    ↓
Append to dataframe
    ↓
Return as JSON
    ↓
Frontend: render table
```

### 4. Visualization Phase
```
GET /api/visualizations/loss-trend
    ↓
Sum loss columns (2001-2024) per year
    ↓
Return years + values
    ↓
Frontend: Chart.js line chart
```

## Key Design Principles

### 1. Anti-Data-Leakage
- RF uses only 2015-2022 features
- Target (2023 loss) excluded from training
- Prevents overfitting to test data

### 2. Modular Architecture
- Separation of concerns (routes, models, utils)
- Easy to add new models
- Independent component testing

### 3. Early Stopping & Regularization
- LSTM: Dropout(0.3), Early stopping (patience 10)
- Prevents overfitting on small datasets
- Reduces training time

### 4. Stateless API (Mostly)
- Models stored in memory during session
- Multiple uploads reset state
- Simplifies deployment

### 5. Frontend-Independent Backend
- Pure REST API (no templates)
- CORS enabled for any frontend
- Easy to swap frontend or add mobile app

## Performance Considerations

### Memory Usage
```
Small dataset (100 municipalities):
  - CSV in memory: ~5 MB
  - LSTM model: ~50 MB
  - Total: ~150 MB

Large dataset (10,000 municipalities):
  - CSV in memory: ~500 MB
  - LSTM model: ~50 MB
  - Total: ~650 MB
```

### Training Time
```
Random Forest (100 est, 10k data):
  - Feature prep: 2-5 sec
  - Training: 10-30 sec
  - Total: 30-40 sec

LSTM (100 epochs, 10k data):
  - Data prep: 5-10 sec
  - Training: 2-5 min
  - Total: 2-6 min
```

### Prediction Speed
```
All models (10k data):
  - RF prediction: <1 sec
  - LSTM regression: <1 sec
  - LSTM classification: <1 sec
  - Total: <3 sec
```

## Error Handling

### Frontend
- Catch Axios errors
- Display user-friendly messages
- Reset UI state on error

### Backend
- Validate input (file type, columns)
- Try-except blocks around model training
- Return HTTP status codes (400, 500)
- Log errors to console

## Scalability

### Current Limitations
- Single server (not distributed)
- Models in memory (not persisted)
- No database (data in CSV)

### Improvement Options
1. Add database (PostgreSQL) for data storage
2. Serialize models with joblib/pickle
3. Implement Redis caching
4. Add Celery task queue for async training
5. Deploy with Gunicorn + Nginx
6. Containerize with Docker

## Testing Strategy

**Unit Tests:**
- Data validation functions
- Feature preparation
- Model prediction

**Integration Tests:**
- Upload endpoint
- Training endpoint
- Prediction consistency

**UI Tests:**
- File upload
- Chart rendering
- Table display

## Security Considerations

1. **File Upload:**
   - Validate file type (CSV only)
   - Check file size (50MB max)
   - Use secure filename

2. **API:**
   - CORS configured
   - No authentication (local only)
   - Input validation

3. **Data:**
   - No sensitive data stored
   - Files deleted after session
   - No logging of data

## Future Enhancements

1. Add authentication/authorization
2. Implement model persistence
3. Add real-time data updates
4. Geospatial visualization (maps)
5. Comparative model analysis
6. Hyperparameter tuning UI
7. Model versioning
8. A/B testing framework
