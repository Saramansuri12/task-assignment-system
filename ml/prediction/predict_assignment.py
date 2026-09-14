from pathlib import Path
import joblib
import pandas as pd


# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "ml"
    / "models"
    / "xgboost_assignment_model.pkl"
)


# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

def load_model():

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found at: {MODEL_PATH}"
        )

    model = joblib.load(MODEL_PATH)

    return model


# --------------------------------------------------
# PREDICT ASSIGNMENT SUCCESS
# --------------------------------------------------

def predict_assignment(model, assignment_data):

    # Convert dictionary into DataFrame
    input_df = pd.DataFrame([assignment_data])

    # Predict success probability
    probability = model.predict_proba(input_df)[0][1]

    # Predict class
    prediction = model.predict(input_df)[0]

    return {
        "success_probability": round(
            float(probability) * 100,
            2
        ),
        "prediction": int(prediction)
    }


# --------------------------------------------------
# MAIN TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("Loading trained model...")

    model = load_model()

    print("Model loaded successfully!")


    # --------------------------------------------------
    # SAMPLE EMPLOYEE + TASK DATA
    # --------------------------------------------------

    assignment_data = {

        "project_domain": "Travel",

        "project_type": "API Development",

        "project_complexity": "Moderate",

        "project_criticality": "Low",

        "role_required": "Backend Developer",

        "team_size_required": 5,

        "estimated_hours": 120,

        "deadline_days": 30,

        "priority": "Medium",

        "skill_match_pct": 85.0,

        "critical_skill_match_pct": 80.0,

        "skill_level_match_pct": 82.0,

        "experience_match_pct": 78.0,

        "domain_match": 1,

        "role_match": 1,

        "critical_project_experience": 1,

        "performance_score": 88.0,

        "current_workload_pct": 40.0,

        "availability_pct": 85.0,

        "reliability_score": 90.0,

        "collaboration_score": 86.0
    }


    # --------------------------------------------------
    # MAKE PREDICTION
    # --------------------------------------------------

    result = predict_assignment(
        model,
        assignment_data
    )


    print("\nASSIGNMENT PREDICTION")

    print("-" * 40)

    print(
        "Success Probability:",
        result["success_probability"],
        "%"
    )

    print(
        "Prediction:",
        "Successful"
        if result["prediction"] == 1
        else "Unsuccessful"
    )