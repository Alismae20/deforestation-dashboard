# Setup & Installation Guide

## Prerequisites Check

Before installation, verify you have:
```powershell
python --version          # Should be 3.8+
pip --version             # Should be 20.0+
```

If not installed, download from https://www.python.org/

## Step-by-Step Installation

### Step 1: Navigate to Project Directory
```powershell
cd C:\Users\aliscia\deforestation-dashboard
```

### Step 2: Create Virtual Environment (Recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

This installs:
- Flask 2.3.2 (Web framework)
- TensorFlow 2.13.0 (Deep learning)
- Scikit-learn 1.3.0 (ML)
- Pandas 2.0.3 (Data processing)
- NumPy 1.24.3
- Werkzeug 2.3.6 (File handling)
- Python-dotenv 1.0.0
- Flask-CORS 4.0.0

⚠️ TensorFlow installation takes 1-2 minutes

### Step 4: Verify Installation
```powershell
python -c "import tensorflow as tf; print(tf.__version__)"
python -c "import sklearn; print(sklearn.__version__)"
```

Both should print version numbers without errors.

## Running the System

### Terminal 1: Start Backend
```powershell
cd C:\Users\aliscia\deforestation-dashboard\backend
python app.py
```

Expected output:
```
Starting Deforestation Dashboard API...
Upload folder: ../uploads
 * Running on http://0.0.0.0:5000
```

### Terminal 2: Start Frontend
```powershell
cd C:\Users\aliscia\deforestation-dashboard\frontend
python app.py
```

Expected output:
```
Starting Deforestation Dashboard Frontend...
 * Running on http://127.0.0.1:8000
```

### Terminal 3: Open Dashboard
```powershell
start http://localhost:8000
```

Or manually open browser to: `http://localhost:8000`

## Stopping the System

1. Press `Ctrl+C` in each terminal running backend/frontend
2. Virtual environment deactivation:
   ```powershell
   deactivate
   ```

## Configuration

### Edit Backend Settings
File: `backend/config.py`

```python
# Change these values as needed:
DEBUG = True                    # Debug mode
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
LSTM_EPOCHS = 100              # Training iterations
LSTM_BATCH_SIZE = 32           # Batch size
RF_ESTIMATORS = 100            # Random Forest trees
```

## Troubleshooting

### Issue: Python command not found
**Solution**: 
- Ensure Python is installed and added to PATH
- Restart terminal after Python installation
- Use full path: `C:\Python311\python.exe app.py`

### Issue: Module not found errors
**Solution**:
- Activate virtual environment: `.\venv\Scripts\Activate.ps1`
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

### Issue: Port 5000 or 8000 already in use
**Solution**:
- Kill existing process: `netstat -ano | findstr :5000`
- Find PID and kill: `taskkill /PID <PID> /F`
- Or edit `frontend/app.py` and change port 8000 to 8001

### Issue: TensorFlow installation fails
**Solution**:
- Update pip first: `pip install --upgrade pip`
- Install CPU version: `pip install tensorflow-cpu`
- Check Python 3.8-3.11 compatibility

### Issue: Out of memory during training
**Solution**:
- Reduce batch size in config.py (32 → 16)
- Reduce LSTM units (32 → 16)
- Reduce number of epochs
- Or use smaller dataset

## Advanced Setup

### Using GPU Acceleration (Optional)
For NVIDIA GPUs:
```powershell
pip install tensorflow-gpu
```

Requires CUDA toolkit (https://developer.nvidia.com/cuda-downloads)

### Running as Service (Windows)
Use NSSM (Non-Sucking Service Manager):
```powershell
nssm install DeforestationBackend "C:\Python311\python.exe" "C:\Users\aliscia\deforestation-dashboard\backend\app.py"
nssm start DeforestationBackend
```

### Docker Deployment
Build Docker image:
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "backend/app.py"]
```

Run:
```powershell
docker build -t deforestation-dashboard .
docker run -p 5000:5000 deforestation-dashboard
```

## Environment Variables

Create `.env` file (optional):
```
FLASK_DEBUG=True
FLASK_ENV=development
API_URL=http://localhost:5000
```

Load in Python:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Next Steps

1. Read README.md for feature overview
2. Check ARCHITECTURE.md for system design
3. See QUICKREF.md for common tasks
4. Review MODELS.md for ML details

## Getting Help

- Check error messages in terminal
- Review logs in `backend/` and `frontend/`
- Run diagnostic script: `python test_api.py`
- See TROUBLESHOOTING.md for common issues
