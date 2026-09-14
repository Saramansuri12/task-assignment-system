def calculate_skill_match(
    employee_skills,
    required_skills
):
    """
    Calculate the percentage of required
    skills possessed by the employee.
    """

    if not required_skills:
        return 0.0

    employee_skills = {
        skill.lower().strip()
        for skill in employee_skills
    }

    required_skills = {
        skill.lower().strip()
        for skill in required_skills
    }

    matched_skills = (
        employee_skills
        &
        required_skills
    )

    match_percentage = (
        len(matched_skills)
        /
        len(required_skills)
    ) * 100

    return round(
        match_percentage,
        2
    )


# --------------------------------------------------
# ROLE MATCH
# --------------------------------------------------

def calculate_role_match(
    employee_role,
    required_role
):

    if not employee_role or not required_role:
        return 0

    employee_role = (
        employee_role
        .lower()
        .strip()
    )

    required_role = (
        required_role
        .lower()
        .strip()
    )

    return int(
        employee_role == required_role
    )


# --------------------------------------------------
# DOMAIN MATCH
# --------------------------------------------------

def calculate_domain_match(
    employee_domains,
    project_domain
):

    if not employee_domains or not project_domain:
        return 0

    employee_domains = {
        domain.lower().strip()
        for domain in employee_domains
    }

    project_domain = (
        project_domain
        .lower()
        .strip()
    )

    return int(
        project_domain
        in
        employee_domains
    )


# --------------------------------------------------
# EXPERIENCE MATCH
# --------------------------------------------------

def calculate_experience_match(
    employee_experience,
    required_experience
):
    """
    Calculate how well employee experience
    matches required experience.
    """

    if required_experience <= 0:
        return 100.0

    match_percentage = (
        employee_experience
        /
        required_experience
    ) * 100

    # Maximum match = 100%
    match_percentage = min(
        match_percentage,
        100
    )

    return round(
        match_percentage,
        2
    )


# --------------------------------------------------
# SKILL LEVEL MATCH
# --------------------------------------------------

def calculate_skill_level_match(
    employee_skill_level,
    required_skill_level
):
    """
    Compare employee skill level
    with required skill level.
    """

    if required_skill_level <= 0:
        return 100.0

    match_percentage = (
        employee_skill_level
        /
        required_skill_level
    ) * 100

    match_percentage = min(
        match_percentage,
        100
    )

    return round(
        match_percentage,
        2
    )


# --------------------------------------------------
# CRITICAL SKILL MATCH
# --------------------------------------------------

def calculate_critical_skill_match(
    employee_skills,
    critical_skills
):

    if not critical_skills:
        return 100.0

    employee_skills = {
        skill.lower().strip()
        for skill in employee_skills
    }

    critical_skills = {
        skill.lower().strip()
        for skill in critical_skills
    }

    matched_skills = (
        employee_skills
        &
        critical_skills
    )

    match_percentage = (
        len(matched_skills)
        /
        len(critical_skills)
    ) * 100

    return round(
        match_percentage,
        2
    )


# --------------------------------------------------
# BUILD ALL MATCHING FEATURES
# --------------------------------------------------

def build_matching_features(
    employee,
    task
):

    employee_skills = (
        employee.get(
            "skills",
            []
        )
    )

    required_skills = (
        task.get(
            "required_skills",
            []
        )
    )

    critical_skills = (
        task.get(
            "critical_skills",
            []
        )
    )

    features = {

        "skill_match_pct":
        calculate_skill_match(
            employee_skills,
            required_skills
        ),

        "critical_skill_match_pct":
        calculate_critical_skill_match(
            employee_skills,
            critical_skills
        ),

        "skill_level_match_pct":
        calculate_skill_level_match(
            employee.get(
                "skill_level",
                0
            ),
            task.get(
                "required_skill_level",
                0
            )
        ),

        "experience_match_pct":
        calculate_experience_match(
            employee.get(
                "years_experience",
                0
            ),
            task.get(
                "required_experience",
                0
            )
        ),

        "domain_match":
        calculate_domain_match(
            employee.get(
                "domains",
                []
            ),
            task.get(
                "project_domain",
                ""
            )
        ),

        "role_match":
        calculate_role_match(
            employee.get(
                "role",
                ""
            ),
            task.get(
                "role_required",
                ""
            )
        )

    }

    return features


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    employee = {

        "skills": [
            "Python",
            "Django",
            "REST API",
            "PostgreSQL"
        ],

        "role": "Backend Developer",

        "domains": [
            "Travel",
            "Finance"
        ],

        "years_experience": 5,

        "skill_level": 8
    }


    task = {

        "required_skills": [
            "Python",
            "Django",
            "REST API"
        ],

        "critical_skills": [
            "Python",
            "Django"
        ],

        "role_required":
        "Backend Developer",

        "project_domain":
        "Travel",

        "required_experience":
        3,

        "required_skill_level":
        7
    }


    features = build_matching_features(
        employee,
        task
    )


    print(
        "\nMATCHING FEATURES"
    )

    print(
        "-" * 40
    )

    for feature, value in features.items():

        print(
            f"{feature}: {value}"
        )