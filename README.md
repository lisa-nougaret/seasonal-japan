# 🌸 When Will Sakura Bloom?
**A data engineering & analytics project to forecast cherry blossom bloom timing, in Japan.*


## ✨ Live Dashboard
▶ [Access dashboard here](https://lisa-nougaret-seasonal-japan-dashboardsapp-8n9yn9.streamlit.app/)

Explore historical climate patterns and predicted sakura bloom dates across Japanese weather stations.

## 📖 Project Overview

Cherry blossom (sakura) bloom is highly sensitive to temperature patterns — especially from the previous autumn and winter.

This project builds an **end-to-end data pipeline and analytical data warehouse** to:
- 🌸 Analyze historical sakura bloom dates
- 🌧 Link bloom timing to climate & precipitation variables
- 📈 Forecast future bloom dates using engineered features

## ☁️ Architecture
```text
JMA Data Sources (climate & sakura)
        ↓
Python ingestion pipeline
        ↓
PostgreSQL (Docker / Neon)
        ↓
SQL transformations
(raw → staging → marts)
        ↓
Feature engineering
        ↓
Prediction model (bloom date)
        ↓
Streamlit dashboard
```

## 🛠️ Tech Stack
| Layer | Tools |
|---------|----------|
| Data ingestion    | Python     |
| Data transformation     | SQL     |
| Data warehouse    | PostgreSQL (Docker / Neon)     | 
| Cloud database    | Neon     | 
| Data modelling    | Star schema     | 
| Feature Engineering    | Python     | 
| Visualization    | Streamlit / Plotly     |
| Environment    | Docker     |  
| Version control   | Git     | 

## ⭐ Data Model
The warehouse uses a star schema optimized for analytics (in progress).

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
**Work in progress.** Current features include station-level and time period filtering, along with historical climate exporation.