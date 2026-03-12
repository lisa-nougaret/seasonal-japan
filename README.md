# 🌸 Seasonal Japan
*A data engineering & analytics project exploring seasonal patterns in Japan.*


This project builds a **data pipeline and analytical data warehouse** to study long-term climate patterns and seasonal phenomena such as:
- 🌸 Cherry blossom bloom timing
- 🍁 Autumn foliage timing
- 🌧 Temperature & precipitation trends
- ❄️ Seasonality and climate anomalies

The goal is to transform raw climate datasets into a **structured analytics model** that can power dashboards and exploratory analysis.

## 🛠️ Tech Stack
| Layer | Tools |
|---------|----------|
| Data ingestion    | Python     |
| Data transformation     | SQL     |
| Data warehouse    | PostgreSQL     | 
| Data modeling    | Star schema     | 
| Visualization    | Plotly     | 
| Version control   | Git     | 

## ⭐ Data Model
The warehouse uses a star schema optimized for analytics.

## 📂 Repository Structure
```text
seasonal-japan/
│
├─ dashboards/        # visualizations
├─ docs/              # diagrams & documentation
├─ notebooks/         # exploration
│
├─ data/
│   ├─ raw/
│   ├─ interim/
│   └─ curated/
│
├─ sql/
│   ├─ staging/       # staging models
│   ├─ marts/         # fact & dimension tables
│   └─ checks/        # data quality tests
│
├─ src/
│   ├─ ingestion/     # data extraction
│   ├─ cleaning/      # data preparation
│   ├─ features/      # feature engineering
│   ├─ pipelines/     # pipeline orchestration
│   └─ viz/           # plotting utilities
│
├─ tests/
│
└─ scripts/
    ├─ run_pipeline.py
    └─ run_checks.py
```

## ✨ Project Status
Work in progress.