from ml.matching.candidate_filter import (
    get_top_candidates
)

from ml.matching.team_formation import (
    form_best_team
)


# ============================================================
# CHECK TEAM VALIDITY
# ============================================================

def is_valid_team(
    team_result,
    required_team_size
):

    if not team_result:
        return False

    team = team_result.get(
        "team"
    )

    coverage = team_result.get(
        "skill_coverage"
    )

    if team is None or team.empty:
        return False

    if coverage is None:
        return False

    # --------------------------------------------------------
    # TEAM SIZE
    # --------------------------------------------------------

    correct_team_size = (
        len(team) == required_team_size
    )

    # --------------------------------------------------------
    # SKILL COVERAGE
    # --------------------------------------------------------

    skill_coverage = float(
        coverage.get(
            "skill_coverage_pct",
            0
        )
    )

    critical_coverage = float(
        coverage.get(
            "critical_skill_coverage_pct",
            0
        )
    )

    full_skill_coverage = (
        skill_coverage >= 100
    )

    full_critical_coverage = (
        critical_coverage >= 100
    )

    return (
        correct_team_size
        and full_skill_coverage
        and full_critical_coverage
    )


# ============================================================
# BUILD ADAPTIVE TEAM
# ============================================================

def build_adaptive_team(
    employees_df,
    task,
    task_skills_df,
    employee_skills_df
):

    task_id = task.get(
        "task_id"
    )

    required_team_size = int(
        task.get(
            "team_size_required",
            1
        )
    )

    print(
        "\nFinding candidate pool..."
    )

    # ========================================================
    # STEP 1 — BUILD CANDIDATE POOL ONCE
    # ========================================================

    candidates = get_top_candidates(

        employees_df=employees_df,

        task_id=task_id,

        task_skills_df=task_skills_df,

        employee_skills_df=employee_skills_df,

        top_n=500
    )

    if candidates is None or candidates.empty:

        print(
            "No candidates found."
        )

        return {
            "team": None,
            "skill_coverage": None,
            "team_score": 0,
            "candidate_pool_size": 0,
            "valid": False
        }

    total_candidates = len(
        candidates
    )

    print(
        f"Candidates available: "
        f"{total_candidates}"
    )

    # ========================================================
    # STEP 2 — SELECT SEARCH SIZES
    # ========================================================
    #
    # We don't need to test every possible size.
    #
    # Old:
    # 30 → 50 → 100 → 200 → 500
    #
    # New:
    # 30 → 100 → 500
    #
    # This reduces expensive calls to form_best_team().
    #
    # ========================================================

    candidate_sizes = []

    # Small initial search
    if total_candidates >= max(
        30,
        required_team_size
    ):

        candidate_sizes.append(
            30
        )

    # Medium search
    if total_candidates >= 100:

        candidate_sizes.append(
            100
        )

    # Full search
    if total_candidates >= 500:

        candidate_sizes.append(
            500
        )
    elif total_candidates > 30:

        candidate_sizes.append(
            total_candidates
        )

    # Remove duplicates
    candidate_sizes = list(
        dict.fromkeys(
            candidate_sizes
        )
    )

    # ========================================================
    # STEP 3 — TRY TEAM FORMATION
    # ========================================================

    for size in candidate_sizes:

        print(
            f"\nTrying top {size} candidates..."
        )

        candidate_pool = (
            candidates.iloc[
                :size
            ].copy()
        )

        team_result = form_best_team(

            candidates_df=
            candidate_pool,

            task=
            task,

            task_skills_df=
            task_skills_df,

            employee_skills_df=
            employee_skills_df
        )

        # ----------------------------------------------------
        # CHECK VALID TEAM
        # ----------------------------------------------------

        if is_valid_team(

            team_result,

            required_team_size
        ):

            print(
                f"Valid team found "
                f"using top {size} candidates."
            )

            team_result[
                "candidate_pool_size"
            ] = size

            team_result[
                "valid"
            ] = True

            return team_result

        # ----------------------------------------------------
        # If team formation produced a result but coverage
        # wasn't perfect, don't retain it as a valid result.
        # ----------------------------------------------------

        print(
            f"No fully valid team "
            f"using top {size} candidates."
        )

    # ========================================================
    # STEP 4 — NO VALID TEAM
    # ========================================================

    print(
        "\nNo fully valid team found."
    )

    return {

        "team":
        None,

        "skill_coverage":
        None,

        "team_score":
        0,

        "candidate_pool_size":
        None,

        "valid":
        False
    }