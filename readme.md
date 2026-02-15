# Predictive Road Degradation Analysis using IoT and Machine Learning

## 📖 Overview
This project presents a predictive road condition monitoring system using accelerometer-based IoT sensor data and machine learning techniques. The goal is to identify road surface conditions (Good, Moderate, Poor) in near real-time to support preventive infrastructure maintenance.

## 🎯 Problem Statement
Traditional road inspection methods rely on manual surveys and visual inspection, which are time-consuming, reactive, and prone to human error. This project proposes a data-driven approach using vibration data and machine learning to continuously assess road quality.

## 🧠 Methodology
1. Data collection from vehicle-mounted accelerometer sensors
2. RMS vibration computation from raw X, Y, Z signals
3. Windowing to segment continuous road data
4. Feature extraction (mean RMS, standard deviation RMS)
5. Data-driven labeling using quantile thresholds
6. Machine learning classification using Random Forest

## 📊 Machine Learning Model
- Algorithm: Random Forest Classifier
- Features: Mean RMS, Standard Deviation RMS
- Output Classes:
  - 0 → Good
  - 1 → Moderate
  - 2 → Poor
- Achieved accuracy: ~95% on test data

## 🔌 IoT Integration (Planned / Ongoing)
An ESP32-based IoT module with an accelerometer sensor will be used to collect real-time vibration data. The trained ML model will classify road conditions in near real-time using the same preprocessing pipeline.

## 📁 Project Structure
raw_data/           → Original sensor datasets
processed_data/     → RMS, windowed, labeled files
rms_analysis.py     → RMS computation
windowing.py        → Feature extraction
labeling.py         → Road condition labeling
merge_data.py       → Dataset merging
train_model.py      → Model training
## 🚀 How to Run
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run pipeline
python rms_analysis.py raw_data/trip1_sensors.csv
python windowing.py processed_data/trip1_sensors_rms.csv
python labeling.py processed_data/trip1_sensors_features.csv
python merge_data.py
python train_model.py