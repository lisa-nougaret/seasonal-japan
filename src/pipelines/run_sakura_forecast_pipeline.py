from src.features.sakura_model_pipeline import (
    load_training_data,
    split_training_data,
    select_best_model,
    evaluate_per_station,
    fit_final_model,
    load_prediction_features,
    build_all_model_predictions,
    save_predictions,
    save_model_artifact,
)

def run_sakura_forecast_pipeline():
    print("Loading training data...")
    train_df = load_training_data()

    if train_df.empty:
        print("No training data found.")
        return

    print(f"Training rows: {len(train_df)}")

    print("Splitting training/test data...")
    X_train, X_test, y_train, y_test, location_codes_test = split_training_data(train_df)

    print("Comparing candidate models...")
    selection_results, best_selection_model = select_best_model(
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test,
    )

    best_model_name = selection_results.iloc[0]["model_name"]
    metrics = selection_results.iloc[0]["metrics"]

    print(f"Best model: {best_model_name}")
    print("Metrics:", metrics)

    print("Evaluating per-station error...")
    per_station = evaluate_per_station(best_selection_model, X_test, y_test, location_codes_test)
    station_maes = sorted(per_station.items(), key=lambda x: x[1]["mae_days"])
    print(f"  Stations evaluated: {len(per_station)}")
    print(f"  Best  station MAE: {station_maes[0][1]['mae_days']:.1f} days ({station_maes[0][0]})")
    print(f"  Worst station MAE: {station_maes[-1][1]['mae_days']:.1f} days ({station_maes[-1][0]})")

    print("Fitting final model on full training data...")
    final_model = fit_final_model(train_df, model_name=best_model_name)

    print("Saving model artifact...")
    model_path = save_model_artifact(
        model=final_model,
        model_name=best_model_name,
        metrics=metrics,
        training_row_count=len(train_df),
        selection_results=selection_results,
        per_station_metrics=per_station,
    )
    print(f"Model saved to: {model_path}")

    print("Loading prediction features...")
    pred_df = load_prediction_features()

    if pred_df.empty:
        print("No prediction rows found.")
        return

    print(f"Prediction rows: {len(pred_df)}")

    print("Building predictions...")
    forecast_df = build_all_model_predictions(
        pred_df=pred_df,
        train_df=train_df,
        selection_results=selection_results,
        per_station_metrics=per_station,
    )

    print("Saving predictions to database...")
    save_predictions(forecast_df)

    print("Forecast pipeline completed successfully.")

if __name__ == "__main__":
    run_sakura_forecast_pipeline()