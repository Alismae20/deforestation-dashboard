"""
API Testing Script
Tests all endpoints without needing the UI
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:5000/api"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.END}")

def test_health():
    """Test API health endpoint"""
    print_header("1. Testing Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_success(f"API is running: {response.json()}")
            return True
        else:
            print_error(f"Unexpected status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API. Make sure backend is running on port 5000")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_upload():
    """Test file upload endpoint"""
    print_header("2. Testing File Upload")
    
    # Create a sample CSV for testing
    sample_csv = """country,subnational1,subnational2,threshold,extent,loss_2001,loss_2002,loss_2003,loss_2004,loss_2005,loss_2006,loss_2007,loss_2008,loss_2009,loss_2010,loss_2011,loss_2012,loss_2013,loss_2014,loss_2015,loss_2016,loss_2017,loss_2018,loss_2019,loss_2020,loss_2021,loss_2022,loss_2023,loss_2024
Brazil,Amazonas,Municipality1,30,1000,10,12,8,15,20,18,22,25,20,28,30,32,28,35,33,30,38,40,36,42,45,48,45,50
Brazil,Amazonas,Municipality2,30,1200,12,14,10,18,22,20,24,27,22,30,32,34,30,37,35,32,40,42,38,44,47,50,47,52
Peru,Loreto,Municipality1,30,800,5,6,4,8,10,9,11,13,10,15,17,18,16,20,19,17,22,24,21,26,29,31,29,33"""
    
    # Write sample CSV
    csv_path = Path("test_data.csv")
    csv_path.write_text(sample_csv)
    
    try:
        with open(csv_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"File uploaded successfully")
            print(f"  Filename: {data['filename']}")
            if 'summary' in data:
                summary = data['summary']
                print(f"  Total municipalities: {summary.get('total_municipalities', 'N/A')}")
                print(f"  Countries: {summary.get('countries', 'N/A')}")
            return True
        else:
            print_error(f"Upload failed: {response.json()}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False
    finally:
        # Cleanup
        if csv_path.exists():
            csv_path.unlink()

def test_data_summary():
    """Test data summary endpoint"""
    print_header("3. Testing Data Summary")
    
    try:
        response = requests.get(f"{BASE_URL}/data-summary")
        if response.status_code == 200:
            data = response.json()
            print_success("Data summary retrieved")
            print(f"  Total municipalities: {data.get('total_municipalities', 'N/A')}")
            print(f"  Countries: {data.get('countries', 'N/A')}")
            print(f"  Models trained: {data.get('models_trained', False)}")
            return True
        else:
            print_error(f"Failed: {response.json()}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_loss_trend():
    """Test loss trend visualization endpoint"""
    print_header("4. Testing Loss Trend Visualization")
    
    try:
        response = requests.get(f"{BASE_URL}/visualizations/loss-trend")
        if response.status_code == 200:
            data = response.json()
            print_success("Loss trend data retrieved")
            years = data.get('years', [])
            values = data.get('loss_values', [])
            print(f"  Years: {years[0]} to {years[-1]}" if years else "  No data")
            print(f"  Total loss: {data.get('total_loss', 0):.2f} ha")
            return True
        else:
            print_error(f"Failed: {response.json()}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_top_municipalities():
    """Test top municipalities endpoint"""
    print_header("5. Testing Top Municipalities")
    
    try:
        response = requests.get(f"{BASE_URL}/visualizations/top-municipalities")
        if response.status_code == 200:
            data = response.json()
            print_success("Top municipalities data retrieved")
            municipalities = data.get('municipalities', [])
            print(f"  Count: {len(municipalities)}")
            if municipalities:
                print(f"  Top: {municipalities[0]}")
            return True
        else:
            print_error(f"Failed: {response.json()}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_train_models():
    """Test model training endpoint"""
    print_header("6. Testing Model Training")
    
    print_info("This may take 3-7 minutes depending on data size...")
    start_time = time.time()
    
    try:
        response = requests.post(f"{BASE_URL}/models/train", timeout=600)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Models trained successfully in {elapsed:.1f}s")
            
            if 'random_forest' in data:
                rf = data['random_forest']
                print(f"  Random Forest Accuracy: {rf.get('accuracy', 0)*100:.2f}%")
            
            if 'lstm_regression' in data:
                lstm_reg = data['lstm_regression']
                print(f"  LSTM Regression R²: {lstm_reg.get('r2_score', 0):.4f}")
            
            if 'lstm_classification' in data:
                lstm_clf = data['lstm_classification']
                print(f"  LSTM Classification Accuracy: {lstm_clf.get('accuracy', 0)*100:.2f}%")
            
            return True
        else:
            print_error(f"Training failed: {response.json()}")
            return False
    except requests.exceptions.Timeout:
        print_error("Training timed out (> 10 minutes)")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_predictions():
    """Test prediction endpoints"""
    print_header("7. Testing Predictions")
    
    endpoints = [
        ('random-forest', 'Random Forest'),
        ('lstm-regression', 'LSTM Regression'),
        ('lstm-classification', 'LSTM Classification')
    ]
    
    all_passed = True
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}/predictions/{endpoint}")
            if response.status_code == 200:
                data = response.json()
                pred_count = len(data.get('predictions', []))
                print_success(f"{name}: {pred_count} predictions retrieved")
            else:
                print_error(f"{name}: {response.json()}")
                all_passed = False
        except Exception as e:
            print_error(f"{name}: {e}")
            all_passed = False
    
    return all_passed

def test_export():
    """Test export endpoint"""
    print_header("8. Testing Export")
    
    try:
        response = requests.get(f"{BASE_URL}/export/predictions")
        if response.status_code == 200:
            data = response.json()
            record_count = len(data.get('data', []))
            print_success(f"Export successful: {record_count} records")
            return True
        else:
            print_error(f"Export failed: {response.json()}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def run_all_tests():
    """Run all tests in sequence"""
    print(f"\n{Colors.BLUE}")
    print("╔" + "═"*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + " API Testing Suite - Deforestation Dashboard ".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "═"*58 + "╝")
    print(f"{Colors.END}")
    
    results = {
        'Health Check': test_health(),
        'File Upload': test_upload(),
        'Data Summary': test_data_summary(),
        'Loss Trend': test_loss_trend(),
        'Top Municipalities': test_top_municipalities(),
        'Model Training': test_train_models(),
        'Predictions': test_predictions(),
        'Export': test_export(),
    }
    
    # Summary
    print_header("Test Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {test_name:<25} {status}")
    
    print(f"\n  Total: {passed}/{total} passed")
    
    if passed == total:
        print_success("All tests passed!")
    else:
        print_error(f"{total - passed} test(s) failed")

if __name__ == '__main__':
    run_all_tests()
