def check_employee_eligibility(
    employee,
    task,
    matching_features
):
    """
    Check whether an employee meets the
    minimum requirements for a task.
    """

    reasons = []


    # ------------------------------------------
    # ROLE MATCH
    # ------------------------------------------

    if matching_features["role_match"] == 0:

        reasons.append(
            "Role does not match task requirement"
        )


    # ------------------------------------------
    # MINIMUM SKILL MATCH
    # ------------------------------------------

    MIN_SKILL_MATCH = 40

    if (
        matching_features["skill_match_pct"]
        < MIN_SKILL_MATCH
    ):

        reasons.append(
            f"Skill match below {MIN_SKILL_MATCH}%"
        )


    # ------------------------------------------
    # CRITICAL SKILL MATCH
    # ------------------------------------------

    MIN_CRITICAL_SKILL_MATCH = 50

    if (
        matching_features[
            "critical_skill_match_pct"
        ]
        < MIN_CRITICAL_SKILL_MATCH
    ):

        reasons.append(
            "Insufficient critical skill match"
        )


    # ------------------------------------------
    # AVAILABILITY
    # ------------------------------------------

    MIN_AVAILABILITY = 20

    availability = employee.get(
        "availability_pct",
        0
    )

    if availability < MIN_AVAILABILITY:

        reasons.append(
            f"Availability below {MIN_AVAILABILITY}%"
        )


    # ------------------------------------------
    # WORKLOAD
    # ------------------------------------------

    MAX_WORKLOAD = 90

    workload = employee.get(
        "current_workload_pct",
        100
    )

    if workload > MAX_WORKLOAD:

        reasons.append(
            f"Workload above {MAX_WORKLOAD}%"
        )


    # ------------------------------------------
    # FINAL RESULT
    # ------------------------------------------

    if reasons:

        return {
            "eligible": False,
            "reasons": reasons
        }


    return {
        "eligible": True,
        "reasons": []
    }