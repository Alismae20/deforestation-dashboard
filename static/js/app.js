/**
 * DEFORESTATION DASHBOARD - MAIN APPLICATION LOGIC
 * Handles file upload, API calls, chart rendering, and UI interactions
 */

// ============================================
// CONFIGURATION
// ============================================

const API_URL = 'http://localhost:5000/api';

// Chart instances for updates
let lossTrendChart = null;
let topMunicipalitiesChart = null;
let trainingHistoryChart = null;

// State
const appState = {
    dataUploaded: false,
    modelsTrained: false,
    chartsRendered: false
};

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkAPIHealth();
});

// ============================================
// EVENT LISTENERS
// ============================================

function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.addEventListener('click', handleNavigation);
    });

    // File upload
    document.getElementById('file-select-btn').addEventListener('click', () => {
        document.getElementById('file-input').click();
    });

    document.getElementById('file-input').addEventListener('change', handleFileSelect);

    // Drag and drop
    const uploadArea = document.getElementById('upload-area');
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // Training
    document.getElementById('train-btn').addEventListener('click', handleTrainModels);

    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', handleTabSwitch);
    });

    // Export
    document.getElementById('export-btn').addEventListener('click', handleExport);
}

// ============================================
// NAVIGATION
// ============================================

function handleNavigation(e) {
    const targetSection = e.target.dataset.section;
    
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    e.target.classList.add('active');

    // Update sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(targetSection).classList.add('active');

    // Load data for specific sections
    if (targetSection === 'explore' && appState.dataUploaded && !appState.chartsRendered) {
        loadExploreData();
    }
    if (targetSection === 'predictions' && appState.modelsTrained) {
        loadPredictions();
    }
}

// ============================================
// FILE UPLOAD
// ============================================

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        uploadFile(file);
    }
}

function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('upload-area').classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('upload-area').classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    document.getElementById('upload-area').classList.remove('dragover');
    
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'text/csv' || file.name.endsWith('.csv')) {
        uploadFile(file);
    } else {
        showError('upload', 'Please drop a CSV file');
    }
}

function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    updateStatus('Uploading file...');

    axios.post(`${API_URL}/upload`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
    .then(response => {
        appState.dataUploaded = true;
        appState.modelsTrained = false;
        appState.chartsRendered = false;

        document.getElementById('file-name').textContent = file.name;
        displayDataSummary(response.data.summary);
        document.getElementById('upload-info').style.display = 'block';
        updateStatus(`✓ File uploaded: ${file.name}`);
    })
    .catch(error => {
        const errorMsg = error.response?.data?.error || error.message;
        showError('upload', errorMsg);
        updateStatus(`✗ Upload failed: ${errorMsg}`, 'error');
    });
}

// ============================================
// DATA SUMMARY DISPLAY
// ============================================

function displayDataSummary(summary) {
    const summaryDiv = document.getElementById('data-summary');
    summaryDiv.innerHTML = `
        <p><strong>Total Municipalities:</strong> ${summary.total_municipalities}</p>
        <p><strong>Countries:</strong> ${summary.countries}</p>
        <p><strong>Total Loss (2001-2024):</strong> ${(summary.total_loss_2001_2024).toFixed(0)} ha</p>
        <p><strong>Average Annual Loss Rate:</strong> ${(summary.avg_loss_rate).toFixed(2)} ha/year</p>
        <p><strong>High Risk Municipalities:</strong> ${summary.high_risk_count}</p>
    `;
}

// ============================================
// EXPLORE DATA
// ============================================

function loadExploreData() {
    loadLossTrendChart();
    loadTopMunicipalitiesChart();
    appState.chartsRendered = true;
}

function loadLossTrendChart() {
    axios.get(`${API_URL}/visualizations/loss-trend`)
        .then(response => {
            const data = response.data;
            const ctx = document.getElementById('loss-trend-chart');

            if (lossTrendChart) lossTrendChart.destroy();

            lossTrendChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.years,
                    datasets: [{
                        label: 'Annual Forest Loss (ha)',
                        data: data.loss_values,
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#2ecc71',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Forest Loss (hectares)'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            showError('explore', 'Failed to load loss trend data');
        });
}

function loadTopMunicipalitiesChart() {
    axios.get(`${API_URL}/visualizations/top-municipalities`)
        .then(response => {
            const data = response.data;
            const ctx = document.getElementById('top-municipalities-chart');

            if (topMunicipalitiesChart) topMunicipalitiesChart.destroy();

            topMunicipalitiesChart = new Chart(ctx, {
                type: 'barHorizontal',
                data: {
                    labels: data.municipalities,
                    datasets: [{
                        label: 'Total Loss 2001-2024 (ha)',
                        data: data.loss_values,
                        backgroundColor: '#3498db',
                        borderColor: '#2980b9',
                        borderWidth: 1
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom'
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true
                        }
                    }
                }
            });
        })
        .catch(error => {
            showError('explore', 'Failed to load top municipalities data');
        });
}

// ============================================
// MODEL TRAINING
// ============================================

function handleTrainModels() {
    if (!appState.dataUploaded) {
        showError('train', 'Please upload data first');
        return;
    }

    const btn = document.getElementById('train-btn');
    btn.disabled = true;
    document.getElementById('train-status').textContent = 'Training models... This may take a few minutes.';
    document.getElementById('train-status').classList.add('loading');

    axios.post(`${API_URL}/models/train`)
        .then(response => {
            appState.modelsTrained = true;

            displayMetrics(
                response.data.random_forest,
                response.data.lstm_regression,
                response.data.lstm_classification
            );

            document.getElementById('metrics-container').style.display = 'block';
            document.getElementById('train-status').textContent = '✓ Models trained successfully!';
            document.getElementById('train-status').classList.remove('loading');
            document.getElementById('train-status').classList.add('success');
            
            btn.disabled = false;
        })
        .catch(error => {
            const errorMsg = error.response?.data?.error || error.message;
            showError('train', errorMsg);
            document.getElementById('train-status').textContent = `✗ Training failed: ${errorMsg}`;
            document.getElementById('train-status').classList.add('error');
            btn.disabled = false;
        });
}

function displayMetrics(rfMetrics, lstmRegMetrics, lstmClfMetrics) {
    // Random Forest metrics
    const rfDiv = document.getElementById('rf-metrics');
    rfDiv.innerHTML = `
        <div class="metric-row">
            <span class="metric-label">Accuracy:</span>
            <span class="metric-value">${(rfMetrics.accuracy * 100).toFixed(2)}%</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Precision:</span>
            <span class="metric-value">${(rfMetrics.precision * 100).toFixed(2)}%</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Recall:</span>
            <span class="metric-value">${(rfMetrics.recall * 100).toFixed(2)}%</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">F1 Score:</span>
            <span class="metric-value">${(rfMetrics.f1_score).toFixed(4)}</span>
        </div>
    `;

    // LSTM Regression metrics
    const lstmRegDiv = document.getElementById('lstm-reg-metrics');
    lstmRegDiv.innerHTML = `
        <div class="metric-row">
            <span class="metric-label">MAE (ha):</span>
            <span class="metric-value">${(lstmRegMetrics.mae).toFixed(2)}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">RMSE (ha):</span>
            <span class="metric-value">${(lstmRegMetrics.rmse).toFixed(2)}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">R² Score:</span>
            <span class="metric-value">${(lstmRegMetrics.r2_score).toFixed(4)}</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Overfitting Gap:</span>
            <span class="metric-value">${(lstmRegMetrics.overfitting_gap).toFixed(4)}</span>
        </div>
    `;

    // LSTM Classification metrics
    const lstmClfDiv = document.getElementById('lstm-clf-metrics');
    lstmClfDiv.innerHTML = `
        <div class="metric-row">
            <span class="metric-label">Accuracy:</span>
            <span class="metric-value">${(lstmClfMetrics.accuracy * 100).toFixed(2)}%</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Precision:</span>
            <span class="metric-value">${(lstmClfMetrics.precision * 100).toFixed(2)}%</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">Recall:</span>
            <span class="metric-value">${(lstmClfMetrics.recall * 100).toFixed(2)}%</span>
        </div>
        <div class="metric-row">
            <span class="metric-label">F1 Score:</span>
            <span class="metric-value">${(lstmClfMetrics.f1_score).toFixed(4)}</span>
        </div>
    `;
}

// ============================================
// PREDICTIONS
// ============================================

function loadPredictions() {
    if (!appState.modelsTrained) {
        showError('predictions', 'Please train models first');
        return;
    }

    loadRandomForestPredictions();
    loadLSTMRegressionPredictions();
    loadLSTMClassificationPredictions();
}

function loadRandomForestPredictions() {
    axios.get(`${API_URL}/predictions/random-forest`)
        .then(response => {
            const predictions = response.data.predictions;
            const table = createPredictionsTable(
                predictions,
                ['country', 'subnational1', 'subnational2', 'predicted_probability', 'risk_label'],
                ['Country', 'Region 1', 'Region 2', 'Probability', 'Risk']
            );
            document.getElementById('rf-table').innerHTML = table;
        })
        .catch(error => {
            showError('predictions', 'Failed to load Random Forest predictions');
        });
}

function loadLSTMRegressionPredictions() {
    axios.get(`${API_URL}/predictions/lstm-regression`)
        .then(response => {
            const predictions = response.data.predictions;
            const table = createPredictionsTable(
                predictions,
                ['country', 'subnational1', 'subnational2', 'tc_loss_ha_2023', 'predicted_loss_2023_ha', 'prediction_error'],
                ['Country', 'Region 1', 'Region 2', 'Actual (ha)', 'Predicted (ha)', 'Error']
            );
            document.getElementById('lstm-reg-table').innerHTML = table;
        })
        .catch(error => {
            showError('predictions', 'Failed to load LSTM Regression predictions');
        });
}

function loadLSTMClassificationPredictions() {
    axios.get(`${API_URL}/predictions/lstm-classification`)
        .then(response => {
            const predictions = response.data.predictions;
            const table = createPredictionsTable(
                predictions,
                ['country', 'subnational1', 'subnational2', 'high_loss_probability', 'predicted_label'],
                ['Country', 'Region 1', 'Region 2', 'Probability', 'Prediction']
            );
            document.getElementById('lstm-clf-table').innerHTML = table;
        })
        .catch(error => {
            showError('predictions', 'Failed to load LSTM Classification predictions');
        });
}

function createPredictionsTable(data, columns, headers) {
    let html = '<thead><tr>';
    headers.forEach(header => {
        html += `<th>${header}</th>`;
    });
    html += '</tr></thead><tbody>';

    data.slice(0, 100).forEach(row => {
        html += '<tr>';
        columns.forEach(col => {
            let value = row[col];
            let cellClass = '';

            if (col === 'risk_label' || col === 'predicted_label') {
                cellClass = value.includes('High') ? 'risk-high' : 'risk-low';
                html += `<td class="${cellClass}">${value}</td>`;
            } else if (typeof value === 'number') {
                html += `<td>${value.toFixed(2)}</td>`;
            } else {
                html += `<td>${value}</td>`;
            }
        });
        html += '</tr>';
    });

    html += '</tbody>';
    return html;
}

// ============================================
// TAB SWITCHING
// ============================================

function handleTabSwitch(e) {
    const tabName = e.target.dataset.tab;

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    e.target.classList.add('active');

    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');
}

// ============================================
// EXPORT
// ============================================

function handleExport() {
    if (!appState.modelsTrained) {
        showError('export', 'Please train models first');
        return;
    }

    const btn = document.getElementById('export-btn');
    btn.disabled = true;
    document.getElementById('export-status').textContent = 'Exporting...';

    axios.get(`${API_URL}/export/predictions`)
        .then(response => {
            const data = response.data.data;
            const json = JSON.stringify(data, null, 2);
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `deforestation_predictions_${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);

            document.getElementById('export-status').textContent = '✓ Predictions exported successfully!';
            document.getElementById('export-status').classList.add('success');
            btn.disabled = false;
        })
        .catch(error => {
            showError('export', 'Failed to export predictions');
            document.getElementById('export-status').classList.add('error');
            btn.disabled = false;
        });
}

// ============================================
// UTILITIES
// ============================================

function showError(section, message) {
    const errorBox = document.getElementById(`${section}-error`);
    errorBox.textContent = `⚠️ ${message}`;
    errorBox.style.display = 'block';
    setTimeout(() => {
        errorBox.style.display = 'none';
    }, 5000);
}

function updateStatus(message, type = 'info') {
    document.getElementById('status-text').textContent = message;
}

function checkAPIHealth() {
    axios.get(`${API_URL}/health`)
        .then(() => {
            updateStatus('✓ Connected to API');
        })
        .catch(() => {
            updateStatus('✗ Cannot connect to API. Start backend server first.');
        });
}
