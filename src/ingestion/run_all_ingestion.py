from src.ingestion.jma_monthly_temp import main as run_monthly_temp
from src.ingestion.jma_sakura import main as run_sakura

from src.ingestion.jma_monthly_temp import main as run_monthly_temp
from src.ingestion.jma_sakura import main as run_sakura

def run_all_ingestion():
    print("Running climate ingestion...")
    run_monthly_temp()

    print("Running sakura ingestion...")
    run_sakura()

    print("All ingestion scripts completed.")

if __name__ == "__main__":
    run_all_ingestion()