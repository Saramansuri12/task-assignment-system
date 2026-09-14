import os
import sys
import pandas as pd

# Add project root to Python path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../..")
    )
)

from ml.data.employee_loader import load_employee_profiles
from ml.matching.skill_engine import load_skill_data
from ml.matching.adaptive_team_builder import build_adaptive_team
from ml.prediction.predict_team_success import (
    load_model,
    predict_team_success
)


# ============================================================
# LOAD ACTUAL TASK DATA
# ============================================================

def load_tasks():
    path = "data/raw/projects_tasks.csv"

    print("Loading actual task data...")

    tasks = pd.read_csv(path)

    print(f"Total tasks available: {len(tasks)}")

    return tasks


# ============================================================
# EVALUATE ONE TASK
# ============================================================

def evaluate_task(
    task,
    employees_df,
    task_skills_df,
    employee_skills_df,
    model
):

    task_id = task["task_id"]

    print("\n" + "=" * 70)
    print(f"Evaluating Task: {task_id}")
    print("=" * 70)

    # --------------------------------------------------------
    # Build adaptive team
    # --------------------------------------------------------

    result = build_adaptive_team(
        employees_df=employees_df,
        task=task,
        task_skills_df=task_skills_df,
        employee_skills_df=employee_skills_df
    )

    # --------------------------------------------------------
    # Check whether valid team exists
    # --------------------------------------------------------

    if not result["valid"]:

        print("\nFAILED: No valid team with full skill coverage found")

        return {
            "task_id": task_id,
            "status": "FAILED",
            "team_size": 0,
            "team_score": 0,
            "skill_coverage": 0,
            "critical_skill_coverage": 0,
            "success_probability": 0,
            "candidate_pool_size": None
        }

    # --------------------------------------------------------
    # Extract team
    # --------------------------------------------------------

    team = result["team"]
    coverage = result["skill_coverage"]

    # --------------------------------------------------------
    # Predict team success
    # --------------------------------------------------------

    success_probability = predict_team_success(
        model=model,
        team=team,
        task=task,
        skill_coverage=coverage
    )

    # --------------------------------------------------------
    # Print results
    # --------------------------------------------------------

    print(f"\nTeam Size: {len(team)}")
    print(f"Team Score: {result['team_score']:.2f}")
    print(
        f"Candidate Pool Used: "
        f"{result['candidate_pool_size']}"
    )

    print(
        f"Skill Coverage: "
        f"{coverage['skill_coverage_pct']:.1f}%"
    )

    print(
        f"Critical Skill Coverage: "
        f"{coverage['critical_skill_coverage_pct']:.1f}%"
    )

    print(
        f"Success Probability: "
        f"{success_probability:.2f}%"
    )

    print("\nSelected Team:")

    display_columns = [
        "employee_id",
        "job_title",
        "candidate_score",
        "skill_match_pct",
        "current_workload_pct",
        "availability_pct"
    ]

    available_columns = [
        col for col in display_columns
        if col in team.columns
    ]

    print(team[available_columns].to_string(index=False))

    return {
        "task_id": task_id,
        "status": "SUCCESS",
        "team_size": len(team),
        "team_score": result["team_score"],
        "skill_coverage": coverage["skill_coverage_pct"],
        "critical_skill_coverage":
            coverage["critical_skill_coverage_pct"],
        "success_probability": success_probability,
        "candidate_pool_size":
            result["candidate_pool_size"]
    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("TASK ASSIGNMENT SYSTEM")
    print("MULTI-TASK TEAM EVALUATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    employees = load_employee_profiles()

    task_skills, employee_skills = load_skill_data()

    tasks = load_tasks()

    print("\nLoading XGBoost model...")

    model = load_model()

    # --------------------------------------------------------
    # Select first 10 REAL tasks
    # --------------------------------------------------------

    test_tasks = tasks.head(10)

    print(
        f"\nTesting {len(test_tasks)} real tasks..."
    )

    results = []

    # --------------------------------------------------------
    # Evaluate tasks
    # --------------------------------------------------------

    for _, task in test_tasks.iterrows():

        result = evaluate_task(
            task=task,
            employees_df=employees,
            task_skills_df=task_skills,
            employee_skills_df=employee_skills,
            model=model
        )

        results.append(result)

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    results_df = pd.DataFrame(results)

    print("\n\n")
    print("=" * 70)
    print("FINAL EVALUATION SUMMARY")
    print("=" * 70)

    print(
        results_df.to_string(index=False)
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    successful = results_df[
        results_df["status"] == "SUCCESS"
    ]

    print("\n" + "=" * 70)
    print("VALIDATION")
    print("=" * 70)

    print(
        f"Successful teams: "
        f"{len(successful)}/{len(results_df)}"
    )

    if len(successful) > 0:

        print(
            "Correct Team Size:",
            (
                successful["team_size"]
                == successful["team_size"].iloc[0]
            ).all()
        )

        print(
            "Full Skill Coverage:",
            (
                successful["skill_coverage"] >= 100
            ).all()
        )

        print(
            "Full Critical Skill Coverage:",
            (
                successful["critical_skill_coverage"] >= 100
            ).all()
        )

    print("\nEvaluation complete.")


if __name__ == "__main__":
    main()