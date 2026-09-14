from sqlalchemy.orm import Session

from app.ml.predictor import AssignmentPredictor

from app.db.models import (
    Employee,
    Task,
    EmployeeSkill,
    TaskSkill,
    Project,
)


class RecommendationEngine:

    def __init__(self, db: Session):

        self.db = db
        self.employee_skills_cache = None
        self.task_skills_cache = {}

        # ML predictor.
        # If the model is not available yet,
        # the engine automatically uses fallback scoring.
        self.predictor = AssignmentPredictor()

    # =========================================================
    # FIND TASK
    # =========================================================

    def get_task(self, task_id: str):

        return (
            self.db.query(Task)
            .filter(
                Task.task_id == task_id
            )
            .first()
        )

    # =========================================================
    # GET EMPLOYEES
    # =========================================================

    def get_employees(self):

        return (
            self.db.query(Employee)
            .all()
        )

    def get_candidate_employees(self, task_id: str):
        required_skill_ids = [
            skill.skill_id
            for skill in self.get_task_skills(task_id)
        ]

        if not required_skill_ids:
            return self.get_employees()

        return (
            self.db.query(Employee)
            .join(
                EmployeeSkill,
                EmployeeSkill.employee_id == Employee.employee_id,
            )
            .filter(EmployeeSkill.skill_id.in_(required_skill_ids))
            .distinct()
            .all()
        )

    # =========================================================
    # GET REQUIRED SKILLS
    # =========================================================

    def get_task_skills(
        self,
        task_id: str,
    ):

        if task_id in self.task_skills_cache:
            return self.task_skills_cache[task_id]

        skills = (
            self.db.query(TaskSkill)
            .filter(
                TaskSkill.task_id == task_id
            )
            .all()
        )

        self.task_skills_cache[task_id] = skills
        return skills

    # =========================================================
    # GET EMPLOYEE SKILLS
    # =========================================================

    def get_employee_skills(
        self,
        employee_id: str,
    ):

        if self.employee_skills_cache is not None:
            return self.employee_skills_cache.get(
                str(employee_id),
                [],
            )

        return (
            self.db.query(EmployeeSkill)
            .filter(
                EmployeeSkill.employee_id
                == employee_id
            )
            .all()
        )

    # =========================================================
    # SKILL MATCH
    # =========================================================

    def calculate_skill_match(
        self,
        employee_id: str,
        task_id: str,
    ):

        required_skills = (
            self.get_task_skills(task_id)
        )

        employee_skills = (
            self.get_employee_skills(
                employee_id
            )
        )

        if not required_skills:
            return 100.0

        employee_skill_ids = set()

        for skill in employee_skills:

            skill_id = getattr(
                skill,
                "skill_id",
                None,
            )

            if skill_id is not None:

                employee_skill_ids.add(
                    str(skill_id)
                )

        matched = 0

        for required in required_skills:

            required_skill_id = getattr(
                required,
                "skill_id",
                None,
            )

            if (
                required_skill_id is not None
                and str(required_skill_id)
                in employee_skill_ids
            ):

                matched += 1

        return round(
            (
                matched
                / len(required_skills)
            )
            * 100,
            2,
        )

    def calculate_skill_features(
        self,
        employee_id: str,
        task_id: str,
    ):
        required_skills = self.get_task_skills(task_id)
        employee_skills = {
            str(skill.skill_id): skill
            for skill in self.get_employee_skills(employee_id)
        }

        if not required_skills:
            return 100.0, 100.0, 100.0

        matched = 0
        critical_required = 0
        critical_matched = 0
        level_scores = []

        for required in required_skills:
            employee_skill = employee_skills.get(str(required.skill_id))
            is_critical = bool(required.is_critical)

            if is_critical:
                critical_required += 1

            if employee_skill is None:
                continue

            matched += 1
            if is_critical:
                critical_matched += 1

            if (
                employee_skill.skill_level is not None
                and required.required_level is not None
                and required.required_level > 0
            ):
                level_scores.append(
                    min(
                        float(employee_skill.skill_level)
                        / float(required.required_level)
                        * 100,
                        100.0,
                    )
                )

        skill_match = matched / len(required_skills) * 100
        critical_match = (
            critical_matched / critical_required * 100
            if critical_required
            else 100.0
        )
        level_match = (
            sum(level_scores) / len(level_scores)
            if level_scores
            else 0.0
        )

        return tuple(round(value, 2) for value in (
            skill_match,
            critical_match,
            level_match,
        ))

    # =========================================================
    # EXPERIENCE SCORE
    # =========================================================

    def calculate_experience_score(
        self,
        employee,
        task,
    ):

        employee_experience = getattr(employee, "years_experience", None)

        required_experience = getattr(
            task,
            "required_experience_years",
            None,
        )

        if employee_experience is None:
            return 50.0

        if required_experience is None:
            return 100.0

        try:

            employee_experience = float(
                employee_experience
            )

            required_experience = float(
                required_experience
            )

        except (
            TypeError,
            ValueError,
        ):

            return 50.0

        if required_experience <= 0:
            return 100.0

        score = (
            employee_experience
            / required_experience
        ) * 100

        return round(
            min(score, 100.0),
            2,
        )

    # =========================================================
    # AVAILABILITY
    # =========================================================

    def calculate_availability(
        self,
        employee,
    ):

        value = getattr(
            employee,
            "availability_pct",
            None,
        )

        if value is None:
            return 70.0

        try:

            return round(
                max(
                    0.0,
                    min(
                        float(value),
                        100.0,
                    ),
                ),
                2,
            )

        except (
            TypeError,
            ValueError,
        ):

            return 70.0

    # =========================================================
    # RELIABILITY
    # =========================================================

    def calculate_reliability(
        self,
        employee,
    ):

        possible_fields = [
            "reliability_score",
            "performance_score",
            "reliability",
        ]

        for field in possible_fields:

            value = getattr(
                employee,
                field,
                None,
            )

            if value is None:
                continue

            try:

                value = float(value)

                if field == "performance_score" and value <= 5:
                    value *= 20

                # Convert 0-1 → 0-100
                if value <= 1:
                    value *= 100

                return round(
                    max(
                        0.0,
                        min(
                            value,
                            100.0,
                        ),
                    ),
                    2,
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

        return 70.0

    def calculate_role_match(self, employee, task):
        employee_role = getattr(employee, "role", None)
        required_role = getattr(task, "role_required", None)

        if not employee_role or not required_role:
            return 0

        return int(
            str(employee_role).strip().lower()
            == str(required_role).strip().lower()
        )

    # =========================================================
    # FALLBACK SCORE
    #
    # Used only when ML model is unavailable.
    # =========================================================

    def calculate_match_score(
        self,
        skill_match,
        experience_match,
        availability,
        reliability,
    ):

        score = (
            skill_match * 0.45
            + experience_match * 0.20
            + availability * 0.20
            + reliability * 0.15
        )

        return round(
            score,
            2,
        )

    # =========================================================
    # ML SCORE
    # =========================================================

    def calculate_ml_score(
        self,
        skill_match,
        experience_match,
        availability,
        reliability,
        features=None,
    ):

        try:

            score = self.predictor.predict(
                skill_match=skill_match,
                experience_match=experience_match,
                availability=availability,
                reliability=reliability,
                features=features,
            )

            return score

        except Exception as exc:

            print(
                f"[ML] Prediction error: {exc}"
            )

            return None

    # =========================================================
    # EXPLANATION
    # =========================================================

    def generate_reason(
        self,
        skill_match,
        experience_match,
        availability,
        reliability,
    ):

        reasons = []

        if skill_match >= 80:

            reasons.append(
                "strong skill match"
            )

        elif skill_match >= 50:

            reasons.append(
                "moderate skill match"
            )

        else:

            reasons.append(
                "limited skill match"
            )

        if experience_match >= 80:

            reasons.append(
                "sufficient experience"
            )

        elif experience_match >= 50:

            reasons.append(
                "reasonable experience"
            )

        if availability >= 80:

            reasons.append(
                "high availability"
            )

        elif availability >= 60:

            reasons.append(
                "good availability"
            )

        else:

            reasons.append(
                "limited availability"
            )

        if reliability >= 80:

            reasons.append(
                "high reliability"
            )

        elif reliability >= 60:

            reasons.append(
                "reliable performance"
            )

        return (
            ", ".join(reasons)
            .capitalize()
        )

    # =========================================================
    # RECOMMEND
    # =========================================================

    def recommend(
        self,
        task_id: str,
        top_k: int = 5,
    ):

        # -----------------------------------------------------
        # 1. FIND TASK
        # -----------------------------------------------------

        task = self.get_task(
            task_id
        )

        if not task:

            return None

        project = (
            self.db.query(Project)
            .filter(Project.project_id == task.project_id)
            .first()
        )

        # -----------------------------------------------------
        # 2. GET EMPLOYEES
        # -----------------------------------------------------

        employees = self.get_candidate_employees(task_id)

        employee_ids = [
            str(employee.employee_id)
            for employee in employees
        ]

        skill_rows = (
            self.db.query(EmployeeSkill)
            .filter(EmployeeSkill.employee_id.in_(employee_ids))
            .all()
        )

        self.employee_skills_cache = {}

        for skill in skill_rows:
            self.employee_skills_cache.setdefault(
                str(skill.employee_id),
                [],
            ).append(skill)

        results = []

        # -----------------------------------------------------
        # 3. SCORE EVERY EMPLOYEE
        # -----------------------------------------------------

        for employee in employees:

            employee_id = str(
                employee.employee_id
            )

            # ---------------------------------------------
            # Skill
            # ---------------------------------------------

            skill_match, critical_skill_match, skill_level_match = (
                self.calculate_skill_features(
                    employee_id,
                    task_id,
                )
            )

            # ---------------------------------------------
            # Experience
            # ---------------------------------------------

            experience_match = (
                self.calculate_experience_score(
                    employee,
                    task,
                )
            )

            # ---------------------------------------------
            # Availability
            # ---------------------------------------------

            availability = (
                self.calculate_availability(
                    employee
                )
            )

            # ---------------------------------------------
            # Reliability
            # ---------------------------------------------

            reliability = (
                self.calculate_reliability(
                    employee
                )
            )

            role_match = self.calculate_role_match(employee, task)
            domain_match = 0

            # ---------------------------------------------
            # ML PREDICTION
            # ---------------------------------------------

            ml_score = (
                self.calculate_ml_score(
                    skill_match,
                    experience_match,
                    availability,
                    reliability,
                    features={
                        "project_domain": getattr(project, "project_domain", None),
                        "project_type": getattr(project, "project_type", None),
                        "project_complexity": getattr(task, "project_complexity", None),
                        "project_criticality": getattr(task, "project_criticality", None),
                        "role_required": getattr(task, "role_required", None),
                        "team_size_required": getattr(task, "team_size_required", None),
                        "estimated_hours": getattr(task, "estimated_hours", None),
                        "deadline_days": getattr(task, "deadline_days", None),
                        "priority": getattr(task, "priority", None),
                        "skill_match_pct": skill_match,
                        "critical_skill_match_pct": critical_skill_match,
                        "skill_level_match_pct": skill_level_match,
                        "experience_match_pct": experience_match,
                        "domain_match": domain_match,
                        "role_match": role_match,
                        "critical_project_experience": getattr(employee, "critical_project_experience", 0),
                        "performance_score": getattr(employee, "performance_score", None),
                        "current_workload_pct": getattr(employee, "current_workload_pct", None),
                        "availability_pct": availability,
                        "reliability_score": reliability,
                        "collaboration_score": reliability,
                    },
                )
            )

            # ---------------------------------------------
            # FALLBACK
            # ---------------------------------------------

            if ml_score is not None:

                match_score = ml_score

                scoring_method = "ML"

            else:

                match_score = (
                    self.calculate_match_score(
                        skill_match,
                        experience_match,
                        availability,
                        reliability,
                    )
                )

                scoring_method = "RULE_BASED"

            # ---------------------------------------------
            # EMPLOYEE NAME
            # ---------------------------------------------

            employee_name = getattr(
                employee,
                "name",
                None,
            )

            if employee_name is None:

                first_name = getattr(
                    employee,
                    "first_name",
                    "",
                )

                last_name = getattr(
                    employee,
                    "last_name",
                    "",
                )

                employee_name = (
                    f"{first_name} {last_name}"
                ).strip()

            if not employee_name:

                employee_name = (
                    f"Employee {employee_id}"
                )

            # ---------------------------------------------
            # EXPLANATION
            # ---------------------------------------------

            reason = self.generate_reason(
                skill_match,
                experience_match,
                availability,
                reliability,
            )

            # ---------------------------------------------
            # RESULT
            # ---------------------------------------------

            results.append(
                {
                    "employee_id": employee_id,

                    "employee_name":
                        employee_name,

                    "match_score":
                        round(
                            match_score,
                            2,
                        ),

                    "skill_match":
                        skill_match,

                    "experience_match":
                        experience_match,

                    "availability_score":
                        availability,

                    "reliability_score":
                        reliability,

                    "reason":
                        reason,

                    "scoring_method":
                        scoring_method,
                }
            )

        # =====================================================
        # 4. SORT
        # =====================================================

        results.sort(
            key=lambda x:
                x["match_score"],
            reverse=True,
        )

        # =====================================================
        # 5. RETURN TOP K
        # =====================================================

        return results[:top_k]