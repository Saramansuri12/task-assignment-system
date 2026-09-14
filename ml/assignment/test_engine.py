from pathlib import Path
import sys
import pandas as pd
import time


# ============================================================
# ADD PROJECT ROOT
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

if str(BASE_DIR) not in sys.path:
    sys.path.append(
        str(BASE_DIR)
    )


from ml.assignment.assignment_engine import (
    get_assignment_engine
)


# ============================================================
# LOAD ONE REAL TASK
# ============================================================

TASK_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "projects_tasks.csv"
)

tasks = pd.read_csv(
    TASK_PATH
)

task = tasks.iloc[0].to_dict()


# ============================================================
# INITIALIZE ENGINE
# ============================================================

print("\nInitializing engine...")

start = time.time()

engine = get_assignment_engine()

initialization_time = (
    time.time() - start
)

print(
    f"\nEngine initialization time: "
    f"{initialization_time:.2f} seconds"
)


# ============================================================
# FIRST RECOMMENDATION
# ============================================================

print("\n" + "=" * 70)
print("FIRST RECOMMENDATION")
print("=" * 70)

start = time.time()

result_1 = engine.assign_team(
    task
)

first_time = (
    time.time() - start
)

print(
    f"\nRecommendation time: "
    f"{first_time:.2f} seconds"
)

print(
    f"Status: {result_1['status']}"
)

print(
    f"Team Size: "
    f"{result_1.get('team_size')}"
)


# ============================================================
# SECOND RECOMMENDATION
# ============================================================

print("\n" + "=" * 70)
print("SECOND RECOMMENDATION")
print("=" * 70)

start = time.time()

result_2 = engine.assign_team(
    task
)

second_time = (
    time.time() - start
)

print(
    f"\nRecommendation time: "
    f"{second_time:.2f} seconds"
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("PERFORMANCE SUMMARY")
print("=" * 70)

print(
    f"Engine initialization: "
    f"{initialization_time:.2f} seconds"
)

print(
    f"First recommendation: "
    f"{first_time:.2f} seconds"
)

print(
    f"Second recommendation: "
    f"{second_time:.2f} seconds"
)