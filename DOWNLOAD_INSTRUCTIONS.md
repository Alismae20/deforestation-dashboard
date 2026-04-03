# Download & Setup Instructions

Complete step-by-step guide to get the Deforestation Dashboard running on your local system.

## Overview

The system consists of:
- **Backend API** (Python Flask + ML models) on port 5000
- **Frontend Dashboard** (HTML/CSS/JavaScript) on port 8000
- **Machine Learning Models** (Random Forest + LSTM)

## Prerequisites

Before starting, ensure you have:

✅ **Windows 10/11** (or macOS/Linux)
✅ **Python 3.8+** installed (https://www.python.org/)
✅ **2GB RAM** minimum
✅ **1GB free disk space**
✅ **Internet connection** (for pip package downloads)

### Verify Python Installation

Open PowerShell or Command Prompt and run:
```powershell
python --version
pip --version
```

Both should show version numbers. If not, download Python from https://www.python.org/

## Step 1: Download/Access Project Files

The project is already created at:
```
C:\Users\aliscia\deforestation-dashboard\
```

Directory structure:
```
deforestation-dashboard/
├── backend/              (Flask API + ML models)
├── frontend/             (Dashboard UI)
├── uploads/              (Uploaded CSV files)
├── requirements.txt      (Python dependencies)
├── README.md            (Feature overview)
├── SETUP_GUIDE.md       (Installation help)
├── ARCHITECTURE.md      (System design)
├── MODELS.md            (ML details)
├── QUICKREF.md          (Quick commands)
├── run.bat              (Windows quick start)
└── run.ps1              (PowerShell quick start)
```

## Step 2: Install Python Dependencies

### Option A: Quick Start (Windows)

Double-click: `run.bat`
```
This will:
1. Install all dependencies
2. Start backend server
3. Start frontend server
4. Open browser
```

### Option B: Manual Installation

Open PowerShell as Administrator and navigate to the project:

```powershell
cd C:\Users\aliscia\deforestation-dashboard
```

Create virtual environment (recommended):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:
```powershell
pip install -r requirements.txt
```

This installs (~1.5 GB download):
- Flask 2.3.2
- TensorFlow 2.13.0
- Scikit-learn 1.3.0
- Pandas 2.0.3
- NumPy 1.24.3
- Chart.js (frontend)
- Axios (frontend)

⏱️ **Installation time: 3-10 minutes** (depends on internet speed)

## Step 3: Start the Backend Server

Open **Terminal 1** (PowerShell or Command Prompt):

```powershell
cd C:\Users\aliscia\deforestation-dashboard\backend
python app.py
```

Expected output:
```
Starting Deforestation Dashboard API...
Upload folder: ../uploads
 * Running on http://0.0.0.0:5000
 * Press CTRL+C to quit
```

✅ Backend is ready when you see "Running on http://0.0.0.0:5000"

## Step 4: Start the Frontend Server

Open **Terminal 2** (new PowerShell or Command Prompt):

```powershell
cd C:\Users\aliscia\deforestation-dashboard\frontend
python app.py
```

Expected output:
```
Starting Deforestation Dashboard Frontend...
 * Running on http://127.0.0.1:8000
 * Press CTRL+C to quit
```

✅ Frontend is ready when you see "Running on http://127.0.0.1:8000"

## Step 5: Access the Dashboard

### Automatic (Browser)

Manually open browser to:
```
http://localhost:8000
```

You should see:
- Green dashboard with sidebar navigation
- "📁 Upload" section ready for CSV
- "Ready to upload CSV" status

## Step 6: Upload Data & Train Models

### Upload CSV

1. Click **"📁 Upload"** in sidebar
2. Drag & drop your CSV file or click "Select File"
3. CSV must contain:
   - Columns: country, subnational1, subnational2, threshold, extent, loss_2001-2024
   - Numeric values for all loss columns
   - Example rows provided in `test_data.csv`

### Train Models

1. Click **"🤖 Train Models"**
2. Click **"Start Training"** button
3. Wait 3-7 minutes (depends on data size)
4. View performance metrics for:
   - Random Forest (Accuracy %)
   - LSTM Regression (R² score)
   - LSTM Classification (Accuracy %)

### View Predictions

1. Click **"🔮 Predictions"**
2. Switch between 3 tabs:
   - Random Forest: Risk classification
   - LSTM Regression: Loss predictions
   - LSTM Classification: Risk probability

### Export Results

1. Click **"💾 Export"**
2. Click "Export All Predictions as JSON"
3. Browser downloads JSON file

## Troubleshooting

### Issue: "Cannot connect to API"

**Cause:** Backend not running

**Solution:**
- Check Terminal 1 - is backend running?
- Start backend: `cd backend && python app.py`
- Verify output: "Running on http://0.0.0.0:5000"

### Issue: "Port 5000 already in use"

**Cause:** Another program using port 5000

**Solution:**
1. Find process using port:
   ```powershell
   netstat -ano | findstr :5000
   ```
2. Kill process:
   ```powershell
   taskkill /PID <PID_NUMBER> /F
   ```
3. Restart backend

### Issue: "Module not found" errors

**Cause:** Dependencies not installed

**Solution:**
```powershell
pip install -r requirements.txt --force-reinstall
```

### Issue: "Out of memory" during training

**Cause:** Large dataset with limited RAM

**Solution:**
1. Edit `backend/config.py`:
   ```python
   LSTM_BATCH_SIZE = 16  # Reduce from 32
   LSTM_EPOCHS = 50      # Reduce from 100
   ```
2. Restart backend and retry

### Issue: CSV upload fails

**Cause:** Invalid file format or missing columns

**Solution:**
- Check column names: country, subnational1, subnational2, threshold, extent, loss_2001-loss_2024
- Ensure all values are numbers (not text)
- No missing values in columns
- File size < 50MB

## Running Tests

Test all API endpoints without UI:

```powershell
cd C:\Users\aliscia\deforestation-dashboard
python test_api.py
```

This tests:
1. Health check
2. File upload
3. Data summary
4. Visualizations
5. Model training
6. Predictions
7. Export

## Stopping the System

To stop all servers:

### Terminal 1 (Backend)
```
Press Ctrl+C
```

### Terminal 2 (Frontend)
```
Press Ctrl+C
```

### Deactivate Virtual Environment (if used)
```powershell
deactivate
```

## Configuration

### Change Model Parameters

Edit `backend/config.py`:

```python
# Faster training (less accurate)
LSTM_EPOCHS = 50           # Default: 100
RF_ESTIMATORS = 50         # Default: 100

# Better accuracy (slower)
LSTM_EPOCHS = 200          # Default: 100
RF_MAX_DEPTH = 15          # Default: 10

# Lower memory usage
LSTM_BATCH_SIZE = 16       # Default: 32
```

### Change Ports

**Backend port (default 5000):**
Edit `backend/app.py` (last line):
```python
app.run(debug=DEBUG, host='0.0.0.0', port=5001)
```

**Frontend port (default 8000):**
Edit `frontend/app.py` (last line):
```python
app.run(debug=True, host='127.0.0.1', port=8001)
```

Also update `frontend/static/js/app.js`:
```javascript
const API_URL = 'http://localhost:5001/api';  // Match backend port
```

## Performance Expectations

| Operation | Time | Memory |
|-----------|------|--------|
| Install deps | 3-10 min | 1.5 GB |
| Start backend | <5 sec | ~100 MB |
| Start frontend | <3 sec | ~50 MB |
| Upload CSV (10k rows) | 2-5 sec | +300 MB |
| Train all models | 3-7 min | +200 MB |
| Get predictions | <3 sec | - |
| Export results | <1 sec | - |

## Next Steps

1. **Learn the system:**
   - Read README.md (features overview)
   - Read ARCHITECTURE.md (system design)
   - Read MODELS.md (ML details)

2. **Customize:**
   - Edit config.py for parameters
   - Modify CSS for styling (frontend/static/css/style.css)
   - Add new features in app.py

3. **Deploy:**
   - See ARCHITECTURE.md for Docker deployment
   - Use Gunicorn for production server
   - Deploy to cloud (AWS, GCP, Azure)

## Support

**Documentation Files:**
- README.md - Features & capabilities
- SETUP_GUIDE.md - Installation details
- ARCHITECTURE.md - System design
- MODELS.md - ML model documentation
- QUICKREF.md - Quick command reference

**Getting Help:**
1. Check the documentation above
2. Review terminal/console errors
3. Run `python test_api.py` to diagnose
4. Check browser console (F12)

## Quick Command Reference

```powershell
# Navigate
cd C:\Users\aliscia\deforestation-dashboard

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start backend
cd backend && python app.py

# Start frontend
cd frontend && python app.py

# Run tests
python test_api.py

# Stop servers
Ctrl+C (in each terminal)
```

## FAQ

**Q: Is an internet connection required?**
A: Only for initial pip install. After that, system runs locally.

**Q: Can I use the same machine for backend and frontend?**
A: Yes, that's the default setup. Two terminals on same machine.

**Q: Can I access from another computer?**
A: Yes, edit frontend/static/js/app.js and change localhost to server IP:
   ```javascript
   const API_URL = 'http://SERVER_IP:5000/api';
   ```

**Q: What if I want to train on different data?**
A: Upload new CSV in dashboard. Models automatically reset.

**Q: How do I save trained models?**
A: Currently models are kept in memory. See ARCHITECTURE.md for persistence options.

**Q: Can I deploy to production?**
A: Yes, see ARCHITECTURE.md for Gunicorn + Nginx setup.

## Version Information

```
Project: Deforestation Detection Dashboard v1.0
Python: 3.8+
TensorFlow: 2.13.0
Scikit-learn: 1.3.0
Pandas: 2.0.3
Flask: 2.3.2
Node.js: Not required (pure JavaScript frontend)
```

---

**You're all set!** Your Deforestation Dashboard is ready to use. 🌍📊

For detailed information, refer to the documentation files in the project directory.
