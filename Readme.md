# 🇱🇦 Laos Disease Statistics Dashboard

A comprehensive interactive dashboard built using Plotly Dash to monitor and visualize disease outbreaks, weather conditions, regional statistics, and public health news in Laos and neighboring countries.

---

## 📊 Overview

This dashboard aggregates multiple public health datasets, weather records, and news articles to provide:

- **Overview of Disease Cases** across regions and time.
- **Key Diseases Analysis** like HPAI-P, ND, IBD, and MG.
- **Comparative Statistics** with neighboring countries (Vietnam & Thailand).
- **Weather Monitoring** for Laos' regions with alerts and trends.
- **News Feed** for the latest global and regional public health updates.

The application dynamically pulls data from Google Sheets and visualizes it with Plotly and Dash Bootstrap Components.

---

## 🚀 Features

- 📍 **Interactive Maps**: Choropleths and pie maps showing disease spread across provinces.
- 📈 **Time Series Graphs**: Trends of disease cases over time.
- 🌦️ **Live Weather Conditions**: Cards and charts with region-wise temperature, humidity, wind, and alerts.
- 📰 **News Search & Filters**: View, search, and filter recent health articles and statements.
- 🌐 **Cross-Country Comparisons**: Charts for analyzing disease categories in Laos and its neighbors.

---


---

## ⚙️ Setup & Installation

### 1. Extract the files

```bash
cd laos_disease_stats_dash
```
### 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---
## 🔐 Environment Configuration
Add a `.env` file with the following content:
```
GOOGLE_CREDENTIALS_JSON={"type": "...", "project_id": "...", ...}  # Paste your Google service account credentials from json API file
```

---

## 🧪 Run the Application
```bash
python app.py
```

Once started, visit `http://127.0.0.1:8050/` in your browser.

---

## 📁 Data Sources
The app reads the following Google Sheets:
1. `laos_data`: Disease cases by date, location, and disease code. 
2. `laos_regions`: Location-to-region mapping. 
3. `weather_data`: Regional weather metrics. 
4. `news_data`: News articles with metadata. 
5. `neighbours_data`: Comparative disease data for Vietnam and Thailand.

---