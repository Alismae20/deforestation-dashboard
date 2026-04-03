# Quick Reference Guide

## Starting the System

### Quick Start (3 steps)
```powershell
# Terminal 1
cd C:\Users\aliscia\deforestation-dashboard\backend
python app.py

# Terminal 2
cd C:\Users\aliscia\deforestation-dashboard\frontend
python app.py

# Browser
start http://localhost:8000
```

## Common Tasks

### Task 1: Upload CSV Data

**File Format:**
```csv
country,subnational1,subnational2,threshold,extent,loss_2001,...,loss_2024
Brazil,Amazonas,Municipality1,30,1000,10,12,8,...,5
```

**In Dashboard:**
1. Click "📁 Upload" in sidebar
2. Drag & drop CSV or click "Select File"
3. View data summary

### Task 2: Train Models

1. Click "🤖 Train Models"
2. Click "Start Training" button
3. Wait 3-7 minutes (depends on data size)
4. View metrics in performance cards

### Task 3: View Predictions

1. Click "🔮 Predictions"
2. Switch between tabs:
   - Random Forest: Risk classification
   - LSTM Regression: Actual loss values
   - LSTM Classification: Risk probability

### Task 4: Export Results

1. Click "💾 Export"
2. Click "Export All Predictions as JSON"
3. Browser downloads JSON file

## Configuration Changes

### File: `backend/config.py`

**Increase Training Data Size:**
```python
LSTM_EPOCHS = 200        # More iterations
LSTM_BATCH_SIZE = 16     # Smaller batches
```

**Faster Training (less accuracy):**
```python
LSTM_EPOCHS = 50         # Fewer iterations
RF_ESTIMATORS = 50       # Fewer trees
```

**More Memory Usage:**
```python
LSTM_BATCH_SIZE = 64     # Larger batches
RF_MAX_DEPTH = 20        # Deeper trees
```

## Port Changes

### Change Backend Port (default 5000)

File: `backend/app.py` (last line)
```python
app.run(debug=DEBUG, host='0.0.0.0', port=5001)  # Changed from 5000
```

Then update frontend: `frontend/static/js/app.js`
```javascript
const API_URL = 'http://localhost:5001/api';  // Changed from 5000
```

### Change Frontend Port (default 8000)

File: `frontend/app.py` (last line)
```python
app.run(debug=True, host='127.0.0.1', port=8001)  # Changed from 8000
```

## API Testing

### Using PowerShell/cURL

**Health Check:**
```powershell
curl http://localhost:5000/api/health
```

**Upload File:**
```powershell
$file = Get-Item "C:\path\to\data.csv"
curl -X POST -F "file=@$file" http://localhost:5000/api/upload
```

**Train Models:**
```powershell
curl -X POST http://localhost:5000/api/models/train
```

**Get RF Predictions:**
```powershell
curl http://localhost:5000/api/predictions/random-forest
```

## Debugging

### View Backend Logs

Terminal 1 (backend running):
```
Errors and outputs appear in terminal
Press Ctrl+C to stop server
```

### View Frontend Logs

Browser Developer Tools (F12):
- Console tab shows JavaScript errors
- Network tab shows API calls
- Application tab shows local storage

### Common Errors

**Error: "Cannot connect to API"**
→ Backend not running. Start it in Terminal 1

**Error: "Models not trained yet"**
→ Click "Train Models" first in dashboard

**Error: "Port 5000 already in use"**
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Error: "Out of memory"**
→ Reduce batch size in config.py

## File Locations

```
Project Root: C:\Users\aliscia\deforestation-dashboard\

Backend:
  - Python code: backend/
  - Config: backend/config.py
  - Models: backend/models/
  - Uploaded CSVs: uploads/

Frontend:
  - HTML: frontend/templates/index.html
  - CSS: frontend/static/css/style.css
  - JavaScript: frontend/static/js/app.js

Documentation:
  - Setup: SETUP_GUIDE.md
  - Architecture: ARCHITECTURE.md
  - Models: MODELS.md
  - This file: QUICKREF.md
```

## Command Cheat Sheet

```powershell
# Navigate
cd C:\Users\aliscia\deforestation-dashboard
cd backend
cd frontend

# Virtual Environment
python -m venv venv
.\venv\Scripts\Activate.ps1
deactivate

# Install/Update
pip install -r requirements.txt
pip install --upgrade pip

# Run Servers
python app.py                    # Backend or Frontend
python backend/app.py            # From root
python test_api.py              # Run tests

# Stop Servers
Ctrl+C                          # In terminal

# Check Status
python -c "import tensorflow as tf; print(tf.__version__)"
python -c "import sklearn; print(sklearn.__version__)"
```

## Model Information

### Random Forest
- **Purpose:** Binary classification (high/low risk)
- **Features:** 8-year loss trend (2015-2022)
- **Training Time:** 30-40 sec
- **Typical Accuracy:** 75-90%
- **Output:** Risk class + probability

### LSTM Regression
- **Purpose:** Predict actual loss value
- **Features:** Normalized 8-year sequence
- **Training Time:** 2-5 minutes
- **Typical R²:** 0.6-0.8
- **Output:** Loss in hectares

### LSTM Classification
- **Purpose:** Probability-based risk prediction
- **Features:** Normalized 8-year sequence
- **Training Time:** 2-5 minutes
- **Typical Accuracy:** 75-85%
- **Output:** Risk probability (0-1)

## Dataset Requirements

**Minimum:**
- 10 municipalities
- 8+ years of loss data
- Columns: country, subnational1, subnational2, threshold, extent, loss_2001-2024

**Recommended:**
- 100+ municipalities
- Complete 2001-2024 data
- No missing values
- Threshold=30 (filtered)

**Maximum Tested:**
- 10,000 municipalities
- ~500MB file size

## Performance Tips

**Faster Training:**
- Use smaller dataset (filter threshold)
- Reduce LSTM epochs (100 → 50)
- Reduce RF trees (100 → 50)

**Better Accuracy:**
- Use more data (>1000 municipalities)
- Increase LSTM epochs (100 → 200)
- Increase RF depth (10 → 15)

**Lower Memory Usage:**
- Reduce batch size (32 → 16)
- Filter municipalities by extent threshold
- Use fewer features

## CSV Validation Rules

✅ **Valid:**
- Columns: country, subnational1, subnational2, threshold, extent, loss_2001-2024
- Numeric values for loss columns
- UTF-8 encoding
- File size < 50MB

❌ **Invalid:**
- Missing required columns
- Non-numeric loss values
- Extra spaces in headers
- Different column order
- File size > 50MB

## Next Steps

1. **Learn More:**
   - Read SETUP_GUIDE.md for installation
   - Read ARCHITECTURE.md for system design
   - Read MODELS.md for ML details

2. **Customize:**
   - Edit config.py for parameters
   - Modify CSS for styling
   - Add new routes in app.py

3. **Deploy:**
   - Use Docker (see ARCHITECTURE.md)
   - Use Gunicorn + Nginx
   - Deploy to cloud (AWS, GCP, Azure)

## Support Resources

- **Documentation:** README.md, SETUP_GUIDE.md, ARCHITECTURE.md
- **Code:** backend/app.py, models/*, static/js/app.js
- **Testing:** test_api.py, browser DevTools (F12)
- **Errors:** Check terminal output + browser console

## Version History

```
v1.0 (Current)
- Random Forest classifier
- LSTM regression
- LSTM classification
- Interactive dashboard
- CSV upload/export
- Model metrics visualization
```
