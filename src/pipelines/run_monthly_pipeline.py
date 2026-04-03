from src.ingestion.run_all_ingestion import run_all_ingestion
from src.pipelines.run_sakura_forecast_pipeline import run_sakura_forecast_pipeline
from scripts.run_pipeline import run_pipeline
from scripts.run_checks import run_checks

def run_monthly_pipeline():
    print("——— Start the monthly pipeline ———")

    print("[1/4] Running ingestion...")
    run_all_ingestion()

    print("[2/4] Running SQL transformations...")
    run_pipeline()

    print("[3/4] Running sakura forecast pipeline...")
    run_sakura_forecast_pipeline()

    print("[4/4] Running data quality checks...")
    run_checks()

    print("——— MONTHLY PIPELINE COMPLETED ———")

if __name__ == "__main__":
    run_monthly_pipeline()