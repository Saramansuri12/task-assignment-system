import pandas as pd


# ============================================================
# SAFE NUMBER
# ============================================================

def safe_float(value, default=0.0):

    try:

        if pd.isna(value):

            return default

        return float(value)

    except (TypeError, ValueError):

        return default


# ============================================================
# BUILD TASK SKILL REQUIREMENTS
# ============================================================

def build_task_requirements(
    task_id,
    task_skills_df
):
    """
    Build task skill requirement dictionaries once.

    This avoids repeatedly filtering task_skills_df during
    team selection.
    """

    task_skills = task_skills_df[

        task_skills_df[
            "task_id"
        ]

        ==

        task_id

    ].copy()


    if task_skills.empty:

        return {

            "required_skills":
            {},

            "critical_skills":
            set()

        }


    required_skills = {}


    critical_skills = set()


    for _, row in task_skills.iterrows():

        skill_id = row[
            "skill_id"
        ]


        required_level = safe_float(

            row.get(
                "required_level",
                0
            )

        )


        is_critical = str(

            row.get(
                "is_critical",
                False
            )

        ).strip().lower()


        required_skills[
            skill_id
        ] = required_level


        if is_critical in {

            "true",
            "1",
            "yes"
        }:

            critical_skills.add(
                skill_id
            )


    return {

        "required_skills":
        required_skills,

        "critical_skills":
        critical_skills
    }


# ============================================================
# BUILD CANDIDATE SKILL CACHE
# ============================================================

def build_candidate_skill_cache(
    candidate_ids,
    employee_skills_df,
    required_skill_ids
):
    """
    Preload only relevant employee skills.

    Result:

    {
        employee_id: {
            skill_id: skill_level
        }
    }
    """

    relevant_skills = employee_skills_df[

        employee_skills_df[
            "employee_id"
        ]

        .isin(
            candidate_ids
        )

        &

        employee_skills_df[
            "skill_id"
        ]

        .isin(
            required_skill_ids
        )

    ][

        [
            "employee_id",
            "skill_id",
            "skill_level"
        ]

    ].copy()


    cache = {

        employee_id:
        {}

        for employee_id in candidate_ids

    }


    if relevant_skills.empty:

        return cache


    for _, row in relevant_skills.iterrows():

        employee_id = row[
            "employee_id"
        ]


        skill_id = row[
            "skill_id"
        ]


        skill_level = safe_float(

            row.get(
                "skill_level",
                0
            )

        )


        # Keep highest level if duplicates exist

        current_level = cache[
            employee_id
        ].get(
            skill_id,
            0
        )


        if skill_level > current_level:

            cache[
                employee_id
            ][
                skill_id
            ] = skill_level


    return cache


# ============================================================
# CALCULATE TEAM COVERAGE FROM CACHE
# ============================================================

def calculate_cached_team_coverage(
    team_ids,
    required_skills,
    critical_skills,
    skill_cache
):
    """
    Fast in-memory coverage calculation.

    No DataFrame filtering.
    """

    total_skills = len(
        required_skills
    )


    if total_skills == 0:

        return {

            "skill_coverage_pct":
            100.0,

            "skill_level_coverage_pct":
            100.0,

            "critical_skill_coverage_pct":
            100.0,

            "missing_skills":
            [],

            "missing_critical_skills":
            []

        }


    covered_skills = set()


    level_covered_skills = set()


    # --------------------------------------------------------
    # COMBINE TEAM SKILLS
    # --------------------------------------------------------

    team_skill_levels = {}


    for employee_id in team_ids:

        employee_skills = skill_cache.get(

            employee_id,

            {}

        )


        for skill_id, skill_level in employee_skills.items():

            current_level = team_skill_levels.get(

                skill_id,

                0

            )


            if skill_level > current_level:

                team_skill_levels[
                    skill_id
                ] = skill_level


    # --------------------------------------------------------
    # CHECK REQUIREMENTS
    # --------------------------------------------------------

    for skill_id, required_level in required_skills.items():

        if skill_id in team_skill_levels:

            covered_skills.add(
                skill_id
            )


            if (

                team_skill_levels[
                    skill_id
                ]

                >=

                required_level

            ):

                level_covered_skills.add(
                    skill_id
                )


    # --------------------------------------------------------
    # MISSING SKILLS
    # --------------------------------------------------------

    missing_skills = list(

        set(
            required_skills.keys()
        )

        -

        level_covered_skills

    )


    missing_critical_skills = list(

        critical_skills

        -

        level_covered_skills

    )


    # --------------------------------------------------------
    # PERCENTAGES
    # --------------------------------------------------------

    skill_coverage_pct = round(

        (
            len(
                covered_skills
            )

            /

            total_skills

        )

        * 100,

        2

    )


    skill_level_coverage_pct = round(

        (
            len(
                level_covered_skills
            )

            /

            total_skills

        )

        * 100,

        2

    )


    if len(
        critical_skills
    ) == 0:

        critical_skill_coverage_pct = (
            100.0
        )

    else:

        critical_skill_coverage_pct = round(

            (

                len(

                    critical_skills

                    &

                    level_covered_skills

                )

                /

                len(
                    critical_skills
                )

            )

            * 100,

            2

        )


    return {

        "skill_coverage_pct":
        skill_coverage_pct,

        "skill_level_coverage_pct":
        skill_level_coverage_pct,

        "critical_skill_coverage_pct":
        critical_skill_coverage_pct,

        "missing_skills":
        missing_skills,

        "missing_critical_skills":
        missing_critical_skills

    }


# ============================================================
# CALCULATE CANDIDATE COMPLEMENT SCORE
# ============================================================

def calculate_fast_complement_score(
    employee,
    current_skill_levels,
    required_skills,
    critical_skills,
    skill_cache
):
    """
    Calculate how much a candidate improves the team.

    Uses dictionaries instead of repeated DataFrame operations.
    """

    employee_id = employee[
        "employee_id"
    ]


    employee_skills = skill_cache.get(

        employee_id,

        {}

    )


    # --------------------------------------------------------
    # COVERAGE GAINS
    # --------------------------------------------------------

    skill_gain = 0


    level_gain = 0


    critical_gain = 0


    for skill_id, required_level in required_skills.items():

        current_level = current_skill_levels.get(

            skill_id,

            0

        )


        employee_level = employee_skills.get(

            skill_id,

            0

        )


        new_level = max(

            current_level,

            employee_level

        )


        # ----------------------------------------------------
        # NEW SKILL COVERAGE
        # ----------------------------------------------------

        if (

            current_level <= 0

            and

            new_level > 0

        ):

            skill_gain += 1


        # ----------------------------------------------------
        # NEW REQUIRED LEVEL COVERAGE
        # ----------------------------------------------------

        if (

            current_level < required_level

            and

            new_level >= required_level

        ):

            level_gain += 1


            if skill_id in critical_skills:

                critical_gain += 1


    total_skills = max(

        len(
            required_skills
        ),

        1

    )


    total_critical_skills = max(

        len(
            critical_skills
        ),

        1

    )


    # Convert gains to percentages

    skill_gain_pct = (

        skill_gain

        /

        total_skills

    ) * 100


    level_gain_pct = (

        level_gain

        /

        total_skills

    ) * 100


    critical_gain_pct = (

        critical_gain

        /

        total_critical_skills

    ) * 100


    # --------------------------------------------------------
    # EMPLOYEE QUALITY
    # --------------------------------------------------------

    reliability = safe_float(

        employee.get(
            "reliability_score",
            0
        )

    )


    performance = safe_float(

        employee.get(
            "performance_score",
            0
        )

    )


    availability = safe_float(

        employee.get(
            "availability_pct",
            0
        )

    )


    workload = safe_float(

        employee.get(
            "current_workload_pct",
            100
        ),

        100

    )


    workload_score = max(

        0,

        100 - workload

    )


    # --------------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------------

    score = (

        critical_gain_pct
        * 0.40

        +

        level_gain_pct
        * 0.25

        +

        skill_gain_pct
        * 0.15

        +

        reliability
        * 0.08

        +

        performance
        * 0.05

        +

        availability
        * 0.04

        +

        workload_score
        * 0.03

    )


    return round(

        score,

        4

    )


# ============================================================
# CALCULATE FINAL TEAM SCORE
# ============================================================

def calculate_final_team_score(
    team,
    coverage,
    task
):

    if team.empty:

        return 0


    avg_reliability = safe_float(

        team[
            "reliability_score"
        ].mean()

    )


    avg_performance = safe_float(

        team[
            "performance_score"
        ].mean()

    )


    avg_availability = safe_float(

        team[
            "availability_pct"
        ].mean()

    )


    avg_workload = safe_float(

        team[
            "current_workload_pct"
        ].mean()

    )


    workload_score = (

        100

        -

        avg_workload

    )


    criticality = str(

        task.get(

            "project_criticality",

            "Medium"

        )

    ).lower()


    # --------------------------------------------------------
    # HIGH / CRITICAL TASK
    # --------------------------------------------------------

    if criticality in {

        "critical",

        "high"

    }:

        score = (

            coverage[
                "critical_skill_coverage_pct"
            ]
            * 0.30

            +

            coverage[
                "skill_level_coverage_pct"
            ]
            * 0.25

            +

            coverage[
                "skill_coverage_pct"
            ]
            * 0.15

            +

            avg_reliability
            * 0.12

            +

            avg_performance
            * 0.08

            +

            avg_availability
            * 0.06

            +

            workload_score
            * 0.04

        )


    # --------------------------------------------------------
    # MEDIUM / LOW TASK
    # --------------------------------------------------------

    else:

        score = (

            coverage[
                "critical_skill_coverage_pct"
            ]
            * 0.22

            +

            coverage[
                "skill_level_coverage_pct"
            ]
            * 0.22

            +

            coverage[
                "skill_coverage_pct"
            ]
            * 0.16

            +

            avg_reliability
            * 0.12

            +

            avg_performance
            * 0.10

            +

            avg_availability
            * 0.10

            +

            workload_score
            * 0.08

        )


    return round(
        score,
        2
    )


# ============================================================
# FORM BEST TEAM
# ============================================================

def form_best_team(
    candidates_df,
    task,
    task_skills_df,
    employee_skills_df
):
    """
    Fast greedy team formation.

    Optimizations:

    1. Task skills loaded once.
    2. Candidate skills loaded once.
    3. Employee skill data cached in memory.
    4. Coverage updated incrementally.
    5. No repeated DataFrame filtering inside loops.
    """

    # --------------------------------------------------------
    # VALIDATE INPUT
    # --------------------------------------------------------

    if candidates_df is None or candidates_df.empty:

        return {

            "team":
            pd.DataFrame(),

            "team_score":
            0,

            "skill_coverage":
            None,

            "reasons": [

                "No candidate employees available."

            ]

        }


    # --------------------------------------------------------
    # TASK INFORMATION
    # --------------------------------------------------------

    task_id = task[
        "task_id"
    ]


    team_size_required = int(

        task.get(

            "team_size_required",

            1

        )

    )


    team_size_required = min(

        team_size_required,

        len(
            candidates_df
        )

    )


    # ========================================================
    # BUILD TASK REQUIREMENTS ONCE
    # ========================================================

    requirements = (

        build_task_requirements(

            task_id,

            task_skills_df

        )

    )


    required_skills = requirements[
        "required_skills"
    ]


    critical_skills = requirements[
        "critical_skills"
    ]


    required_skill_ids = set(

        required_skills.keys()

    )


    # ========================================================
    # BUILD SKILL CACHE ONCE
    # ========================================================

    candidate_ids = (

        candidates_df[
            "employee_id"
        ]

        .tolist()

    )


    skill_cache = (

        build_candidate_skill_cache(

            candidate_ids,

            employee_skills_df,

            required_skill_ids

        )

    )


    # ========================================================
    # INITIALIZE TEAM
    # ========================================================

    selected_employee_ids = []


    remaining_candidates = (
        candidates_df.copy()
    )


    # Current maximum skill level available
    # for each required skill

    current_skill_levels = {}


    # ========================================================
    # FAST GREEDY TEAM SELECTION
    # ========================================================

    while (

        len(
            selected_employee_ids
        )

        <

        team_size_required

        and

        not remaining_candidates.empty

    ):


        best_employee_id = None


        best_score = float(
            "-inf"
        )


        # ----------------------------------------------------
        # EVALUATE CANDIDATES
        # ----------------------------------------------------

        for _, employee in remaining_candidates.iterrows():

            score = (

                calculate_fast_complement_score(

                    employee=

                    employee,

                    current_skill_levels=

                    current_skill_levels,

                    required_skills=

                    required_skills,

                    critical_skills=

                    critical_skills,

                    skill_cache=

                    skill_cache

                )

            )


            if score > best_score:

                best_score = score


                best_employee_id = (

                    employee[
                        "employee_id"
                    ]

                )


        # ----------------------------------------------------
        # STOP IF NO CANDIDATE
        # ----------------------------------------------------

        if best_employee_id is None:

            break


        # ----------------------------------------------------
        # ADD EMPLOYEE
        # ----------------------------------------------------

        selected_employee_ids.append(

            best_employee_id

        )


        # ----------------------------------------------------
        # UPDATE TEAM SKILLS INCREMENTALLY
        # ----------------------------------------------------

        selected_skills = skill_cache.get(

            best_employee_id,

            {}

        )


        for skill_id, skill_level in selected_skills.items():

            current_level = (

                current_skill_levels.get(

                    skill_id,

                    0

                )

            )


            if skill_level > current_level:

                current_skill_levels[
                    skill_id
                ] = skill_level


        # ----------------------------------------------------
        # REMOVE SELECTED EMPLOYEE
        # ----------------------------------------------------

        remaining_candidates = (

            remaining_candidates[

                remaining_candidates[
                    "employee_id"
                ]

                !=

                best_employee_id

            ]

        )


    # ========================================================
    # BUILD FINAL TEAM
    # ========================================================

    team = (

        candidates_df[

            candidates_df[
                "employee_id"
            ]

            .isin(
                selected_employee_ids
            )

        ]

        .copy()

    )


    # ========================================================
    # FINAL COVERAGE
    # ========================================================

    final_coverage = (

        calculate_cached_team_coverage(

            selected_employee_ids,

            required_skills,

            critical_skills,

            skill_cache

        )

    )


    # ========================================================
    # FINAL TEAM SCORE
    # ========================================================

    team_score = (

        calculate_final_team_score(

            team,

            final_coverage,

            task

        )

    )


    # ========================================================
    # BUILD REASONS
    # ========================================================

    reasons = [

        (

            f"Team size selected: "
            f"{len(team)}"

        ),

        (

            f"Skill coverage: "
            f"{final_coverage['skill_coverage_pct']}%"

        ),

        (

            f"Skill-level coverage: "
            f"{final_coverage['skill_level_coverage_pct']}%"

        ),

        (

            f"Critical skill coverage: "
            f"{final_coverage['critical_skill_coverage_pct']}%"

        )

    ]


    # --------------------------------------------------------
    # CRITICAL SKILLS STATUS
    # --------------------------------------------------------

    if (

        final_coverage[
            "missing_critical_skills"
        ]

    ):

        reasons.append(

            "Some critical skills are still missing."

        )

    else:

        reasons.append(

            "All critical skills are covered."

        )


    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {

        "team":
        team,

        "team_score":
        team_score,

        "skill_coverage":
        final_coverage,

        "reasons":
        reasons
    }