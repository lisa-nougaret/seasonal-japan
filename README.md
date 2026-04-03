# 🌸 When Will Sakura Bloom?

**An end-to-end data engineering & analytics project to forecast sakura (cherry blossom) bloom timing in Japan.*

## ✨ Live Dashboard

▶ [Access dashboard here](https://lisa-nougaret-seasonal-japan-dashboardsapp-8n9yn9.streamlit.app/)

Explore historical climate patterns and predicted sakura bloom dates across Japanese weather stations.

## 📖 Project Overview

Sakura bloom is highly sensitive to temperature patterns — particularly during the previous autumn and winter.

This project builds a **complete data pipeline and analytical platform** to:
- 🌸 Analyze historical sakura bloom dates
- 🌧 Link bloom timing to climate & precipitation variables
- 🧠 Engineer predictive features from seasonal trends
- 📈 Forecast future bloom dates using machine learning

## ☁️ Architecture

```text
JMA Data Sources (climate & sakura)
        ↓
Python ingestion pipeline (web scraping)
        ↓
PostgreSQL (Docker local / Neon cloud)
        ↓
SQL transformations
(raw → staging → analytics)
        ↓
Feature engineering
        ↓
Machine learning model (bloom date)
        ↓
Streamlit dashboard
```

## 🔄️ Pipeline Automation

This pipeline is fully automated using GitHub Actions: 
- 📅 Monthly, 15th of each month
- ⚙️ Executes:
        - Data ingestion (JMA climate & sakura data)
        - Data transformation (SQL models)
        - Feature engineering
        - Model training & evaluation
        - Forecast generation
        - Database update (Neon PostgreSQL)

## 🛠️ Tech Stack

| Layer | Tools |
|---------|----------|
| Data ingestion    | Python     |
| Data transformation     | SQL     |
| Data warehouse    | PostgreSQL (Docker / Neon)     | 
| Cloud database    | Neon     | 
| Data modelling    | Star schema     | 
| Feature Engineering    | Python     | 
| Machine Learning    | scikit-learn     | 
| Visualization    | Streamlit / Plotly     |
| Orchestration    | GitHub Actions     |
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
├─ scripts/
│   ├─ run_pipeline.py
│   └─ run_checks.py
│
└─ .github/workflows/
    └─ monthly_pipeline.yml   # automated pipeline
```

## 🌠 Key Features

- End-to-end data pipeline (ingestion → modelling → prediction)
- Automated monthly updates
- Feature engineering based on seasonal climate patterns
- Machine learning model for bloom date prediction
- Interactive dashboard for exploration and insights

## ✨ Project Status

**Work in progress.** Future improvements features include automated data quality checks, advanced models, incremental data ingestion, and enhanced app design.