# 🌸 Seasonal Japan
*A data engineering & analytics project exploring seasonal patterns in Japan.*


## ✨ Live Dashboard
▶ [Access dashboard here](https://lisa-nougaret-seasonal-japan-dashboardsapp-8n9yn9.streamlit.app/)

Explore long-term monthly climate patterns across Japanese weather stations through an interactive dashboard.

## 📖 Project Overview

This project builds an **end-to-end data pipeline and analytical data warehouse** to study long-term climate patterns and seasonal phenomena such as:
- 🌸 Cherry blossom bloom timing
- 🍁 Autumn foliage timing
- 🌧 Temperature & precipitation trends
- ❄️ Seasonality and climate anomalies

## ☁️ Architecture
```text
Markdown README (JMA Climate Data)
        ↓
Python ingestion pipeline
        ↓
PostgreSQL (local Docker database)
        ↓
SQL transformations
(staging → marts)
        ↓
Analytics warehouse
(star schema)
        ↓
Neon cloud database
        ↓
Streamlit dashboard
```

## 🛠️ Tech Stack
| Layer | Tools |
|---------|----------|
| Data ingestion    | Python     |
| Data transformation     | SQL     |
| Data warehouse    | PostgreSQL     | 
| Cloud database    | Neon     | 
| Data modeling    | Star schema     | 
| Visualization    | Streamlit & Plotly     |
| Environment    | Docker     |  
| Version control   | Git     | 

## ⭐ Data Model
The warehouse uses a star schema optimized for analytics — fact_monthly climate, dim_station, and dim_date.

## 📂 Repository Structure
```text
seasonal-japan/
│
├─ dashboards/        # Streamlit dashboard
├─ docs/              # diagrams & documentation
├─ notebooks/         # exploratory analysis
│
├─ data/
│   ├─ raw/           # source datasets
│   ├─ interim/       # intermediate datasets
│   └─ curated/       # cleaned outputs
│
├─ sql/
│   ├─ staging/       # staging transformations
│   ├─ marts/         # fact & dimension models
│   └─ checks/        # data quality tests
│
├─ src/
│   ├─ ingestion/     # data extraction scripts
│   ├─ cleaning/      # data preparation
│   ├─ features/      # feature engineering
│   ├─ pipelines/     # pipeline orchestration
│   └─ viz/           # dashboard queries
│
├─ tests/
│
└─ scripts/
    ├─ run_pipeline.py
    └─ run_checks.py
```

## ✨ Project Status
Work in progress — planned improvements include incorporating sakura bloom & foliage datasets, automated pipeline scheduling, and predictive analytics.