from src.features.sakura_model_pipeline import (
    load_training_data,
    split_training_data,
    train_linear_model,
    evaluate_model,
    fit_final_model,
    load_prediction_features,
    build_predictions,
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
    X_train, X_test, y_train, y_test = split_training_data(train_df)

    print("Training evaluation model...")
    eval_model = train_linear_model(X_train, y_train)

    print("Evaluating model...")
    metrics = evaluate_model(eval_model, X_test, y_test)
    print("Metrics:", metrics)

    print("Fitting final model on full training data...")
    final_model = fit_final_model(train_df)

    print("Saving model artifact...")
    model_path = save_model_artifact(
        final_model,
        metrics=metrics,
        training_row_count=len(train_df),
    )
    print(f"Model saved to: {model_path}")

    print("Loading prediction features...")
    pred_df = load_prediction_features()

    if pred_df.empty:
        print("No prediction rows found.")
        return

    print(f"Prediction rows: {len(pred_df)}")

    print("Building predictions...")
    forecast_df = build_predictions(
        pred_df=pred_df,
        model=final_model,
        metrics=metrics,
        training_row_count=len(train_df),
    )

    print("Saving predictions to database...")
    save_predictions(forecast_df)

    print("Forecast pipeline completed successfully.")

if __name__ == "__main__":
    run_sakura_forecast_pipeline()