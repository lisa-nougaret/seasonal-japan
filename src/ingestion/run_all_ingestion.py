from src.ingestion.jma_monthly_temp import main as run_monthly_temp
from src.ingestion.jma_sakura import main as run_sakura
from src.ingestion.jma_station_metadata import load_station_metadata

def run_all_ingestion():
    
    print("Running climate ingestion...")
    run_monthly_temp()

    print("Running sakura ingestion...")
    run_sakura()

    print("Running station metadata ingestion...")
    load_station_metadata()

    print("All ingestion scripts completed.")

if __name__ == "__main__":
    run_all_ingestion()