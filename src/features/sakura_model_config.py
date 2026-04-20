TARGET = "day_of_year"

FEATURES = [
    "last_autumn_mean_temp",
    "winter_mean_temp",
    "january_mean_temp",
    "february_mean_temp",
    "march_mean_temp",
    "january_march_cumulative_temp",
]

MODEL_VERSION = "v3"
EVALUATION_METRIC = "mae_days"

CANDIDATE_MODELS = {
    "linear_regression": {
        "hyperparameters": {}
    },
    "random_forest": {
        "hyperparameters": {
            "n_estimators": 300,
            "max_depth": 10,
            "min_samples_split": 10,
            "min_samples_leaf": 5,
            "random_state": 42,
            "n_jobs": -1
        }
    },
    "hist_gradient_boosting": {
        "hyperparameters": {
            "learning_rate": 0.05,
            "max_iter": 300,
            "max_depth": 6,
            "min_samples_leaf": 20,
            "random_state": 42
        }
    }
}