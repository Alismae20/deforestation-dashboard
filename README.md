# Deforestation Detection Dashboard

A comprehensive web-based system for detecting and predicting forest loss using advanced machine learning and deep learning models.

## Features

✨ **Core Capabilities**
- **CSV Data Upload** - Import forest loss data (2001-2024)
- **Random Forest Classification** - Predict high/low deforestation risk
- **LSTM Regression** - Forecast actual forest loss values
- **LSTM Classification** - Probability-based risk assessment with early stopping regularization
- **Interactive Dashboard** - Real-time visualizations and predictions
- **Data Export** - Download all predictions as JSON

📊 **Visualizations**
- Annual forest loss trends (2001-2024)
- Top 10 municipalities by cumulative loss
- Training history and model performance metrics
- Prediction comparison tables

🔧 **Technical Stack**
- **Backend**: Flask 2.3.2, TensorFlow 2.13.0, Scikit-learn 1.3.0, Pandas 2.0.3
- **Frontend**: HTML5, CSS3, Vanilla JavaScript, Chart.js 3.9.1
- **Architecture**: Modular design with anti-data-leakage safeguards

## Quick Start

### Prerequisites
- Python 3.8+
- Windows/macOS/Linux
- 2GB RAM minimum
- 1GB free disk space

### Installation

1. **Navigate to project folder**
   ```powershell
   cd C:\Users\aliscia\deforestation-dashboard
   ```

2. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Start backend server** (Terminal 1)
   ```powershell
   cd backend
   python app.py
   ```
   Server runs on `http://localhost:5000`

4. **Start frontend server** (Terminal 2)
   ```powershell
   cd frontend
   python app.py
   ```
   Dashboard available at `http://localhost:8000`

5. **Use the dashboard**
   - Open browser: `http://localhost:8000`
   - Upload your CSV file
   - Train models
   - View predictions

## CSV Data Format

Required columns:
```
country, subnational1, subnational2, threshold, extent, 
loss_2001, loss_2002, ..., loss_2024
```

Example:
```csv
Brazil,Amazonas,Municipality1,30,1000,10,12,8,...,5
```

## Models

### Random Forest Classifier
- **Task**: Predict high/low 2023 forest loss
- **Features**: 8-year loss trend (2015-2022) + extent metrics
- **Architecture**: 100 estimators, max_depth=10
- **Metrics**: Accuracy, Precision, Recall, F1, Confusion Matrix

### LSTM Regression
- **Task**: Predict actual 2023 loss value (hectares)
- **Features**: Normalized 8-year time-series (2015-2022)
- **Architecture**: LSTM(32) → LSTM(16) → Dense layers
- **Regularization**: Dropout(0.3), Early Stopping (patience=10)
- **Metrics**: MAE, RMSE, R², Overfitting Gap

### LSTM Classification
- **Task**: Predict high/low risk probability
- **Features**: Same normalized time-series
- **Architecture**: Identical to regression with sigmoid output
- **Loss**: Binary crossentropy
- **Metrics**: Accuracy, Precision, Recall, F1

## API Endpoints

### File Management
- `POST /api/upload` - Upload CSV file
- `GET /api/data-summary` - Get data statistics

### Model Training
- `POST /api/models/train` - Train all 3 models

### Visualizations
- `GET /api/visualizations/loss-trend` - Annual loss trend
- `GET /api/visualizations/top-municipalities` - Top 10 municipalities

### Predictions
- `GET /api/predictions/random-forest` - RF predictions
- `GET /api/predictions/lstm-regression` - LSTM regression predictions
- `GET /api/predictions/lstm-classification` - LSTM classification predictions

### Export
- `GET /api/export/predictions` - Export all predictions

## Project Structure

```
deforestation-dashboard/
├── backend/
│   ├── app.py                 # Flask API server
│   ├── config.py              # Configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── random_forest.py   # RF classifier
│   │   └── lstm_model.py      # LSTM models
│   └── utils/
│       ├── __init__.py
│       └── data_handler.py    # CSV handling
├── frontend/
│   ├── app.py                 # Flask web server
│   ├── templates/
│   │   └── index.html         # Dashboard UI
│   └── static/
│       ├── css/
│       │   └── style.css      # Styling
│       └── js/
│           └── app.js         # UI logic
├── uploads/                   # Uploaded CSV files
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## Configuration

Edit `backend/config.py` to customize:
- Maximum upload file size (50MB default)
- LSTM training parameters (epochs, patience, batch size)
- Random Forest hyperparameters
- Data filtering thresholds

## Troubleshooting

**Issue: "Cannot connect to API"**
- Ensure backend is running on port 5000
- Check firewall settings

**Issue: "Models training fails with memory error"**
- Reduce batch size in `config.py`
- Reduce number of LSTM units

**Issue: CSV upload fails**
- Verify column names match required format
- Ensure CSV is properly formatted (no extra spaces)
- Check file size < 50MB

## Performance

| Model | Training Time | Prediction Time | Accuracy |
|-------|---------------|-----------------|----------|
| Random Forest | 10-30 sec | <1 sec | 75-90% |
| LSTM Regression | 2-5 min | <1 sec | RMSE varies |
| LSTM Classification | 2-5 min | <1 sec | 75-85% |

*Times vary based on data size and system specs*

## Known Limitations

- Maximum 100k municipalities per upload
- Time-series features require minimum 8 years of data
- LSTM models prefer normalized data

## Development

### Running Tests
```powershell
python test_api.py
```

### Adding Custom Models
1. Create model in `backend/models/`
2. Implement `train()` and `predict_all()` methods
3. Add route in `backend/app.py`
4. Update frontend UI in `frontend/static/js/app.js`

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check SETUP_GUIDE.md
2. Review ARCHITECTURE.md
3. See QUICKREF.md for common tasks

## Citation

If you use this dashboard in your research, please cite:
```
Deforestation Detection Dashboard v1.0 (2024)
Built with LSTM and Random Forest ML models
```
