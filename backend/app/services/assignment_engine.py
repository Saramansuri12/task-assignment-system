from sqlalchemy.orm import Session

from app.db.models.employee import Employee
from app.db.models.employee_skills import EmployeeSkill
from app.db.models.skill import Skill


class AssignmentEngine:
    """
    Rule-based employee assignment engine.

    ML can be plugged into this layer later.
    """

    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------
    # Get employees
    # ---------------------------------------------------------

    def get_available_employees(self):

        employees = (
            self.db.query(Employee)
            .filter(
                Employee.availability_pct > 0,
                Employee.current_workload_pct < 100
            )
            .all()
        )

        return employees

    # ---------------------------------------------------------
    # Get employee skills
    # ---------------------------------------------------------

    def get_employee_skills(self, employee_id):

        rows = (
            self.db.query(
                EmployeeSkill,
                Skill
            )
            .join(
                Skill,
                EmployeeSkill.skill_id == Skill.skill_id
            )
            .filter(
                EmployeeSkill.employee_id == employee_id
            )
            .all()
        )

        skills = {}

        for employee_skill, skill in rows:

            skills[str(skill.skill_id)] = {
                "name": skill.skill_name,
                "level": employee_skill.skill_level
            }

        return skills

    # ---------------------------------------------------------
    # Calculate skill match
    # ---------------------------------------------------------

    def calculate_skill_match(
        self,
        employee_id,
        required_skills
    ):

        if not required_skills:
            return 0.0

        employee_skills = self.get_employee_skills(
            employee_id
        )

        matched = 0

        for required_skill in required_skills:

            skill_id = str(
                required_skill["skill_id"]
            )

            required_level = float(
                required_skill.get(
                    "required_level",
                    0
                )
            )

            employee_skill = employee_skills.get(
                skill_id
            )

            if employee_skill is None:
                continue

            employee_level = float(
                employee_skill.get(
                    "level",
                    0
                )
            )

            if employee_level >= required_level:
                matched += 1

        return (
            matched / len(required_skills)
        ) * 100

    # ---------------------------------------------------------
    # Workload score
    # ---------------------------------------------------------

    def calculate_workload_score(
        self,
        employee
    ):

        workload = employee.current_workload_pct or 0
        availability = employee.availability_pct or 0

        # Lower workload = better.
        workload_score = 100 - workload

        # Combine workload and availability.
        score = (
            workload_score * 0.6
            +
            availability * 0.4
        )

        return max(
            0,
            min(100, score)
        )

    # ---------------------------------------------------------
    # Experience score
    # ---------------------------------------------------------

    def calculate_experience_score(
        self,
        employee,
        required_experience
    ):

        if not required_experience:
            return 100.0

        employee_experience = (
            employee.years_experience or 0
        )

        if employee_experience >= required_experience:
            return 100.0

        if required_experience == 0:
            return 100.0

        return (
            employee_experience
            /
            required_experience
        ) * 100

    # ---------------------------------------------------------
    # Performance score
    # ---------------------------------------------------------

    def calculate_performance_score(
        self,
        employee
    ):

        score = employee.performance_score

        if score is None:
            return 50.0

        return max(
            0,
            min(100, float(score))
        )

    # ---------------------------------------------------------
    # GET TASK REQUIRED SKILLS
    # ---------------------------------------------------------

    def get_task_required_skills(
        self,
        task_id
    ):

        from app.db.models import TaskSkill

        rows = (
            self.db.query(TaskSkill)
            .filter(
                TaskSkill.task_id == task_id
            )
            .all()
        )

        required_skills = []

        for row in rows:

            required_skills.append({
                "skill_id": str(row.skill_id),

                "required_level": float(
                    row.required_level or 0
                ),

                "is_critical": bool(
                    getattr(
                        row,
                        "is_critical",
                        False
                    )
                )
            })

        return required_skills

    # ---------------------------------------------------------
    # RECOMMEND EMPLOYEES FOR A TASK
    # ---------------------------------------------------------

    def recommend_for_task(
        self,
        task_id,
        top_k=10
    ):

        from app.db.models import Task

        task = (
            self.db.query(Task)
            .filter(
                Task.task_id == task_id
            )
            .first()
        )

        if not task:
            return None

        required_skills = (
            self.get_task_required_skills(
                task_id
            )
        )

        required_experience = (
            task.required_experience_years or 0
        )

        recommendations = self.rank_employees(
            required_skills=required_skills,
            required_experience=required_experience,
            top_k=top_k
        )

        return {
            "task_id": str(task_id),

            "required_skills":
                required_skills,

            "required_experience_years":
                required_experience,

            "recommendations":
                recommendations
        }

    # ---------------------------------------------------------
    # Final rule-based score
    # ---------------------------------------------------------

    def calculate_final_score(
        self,
        skill_match,
        workload_score,
        experience_score,
        performance_score
    ):

        score = (
            skill_match * 0.40
            +
            workload_score * 0.20
            +
            experience_score * 0.15
            +
            performance_score * 0.25
        )

        return round(score, 2)

    # ---------------------------------------------------------
    # Rank employees
    # ---------------------------------------------------------

    def rank_employees(
        self,
        required_skills,
        required_experience=0,
        top_k=10
    ):

        employees = (
            self.get_available_employees()
        )

        results = []

        for employee in employees:

            skill_match = (
                self.calculate_skill_match(
                    employee.employee_id,
                    required_skills
                )
            )

            workload_score = (
                self.calculate_workload_score(
                    employee
                )
            )

            experience_score = (
                self.calculate_experience_score(
                    employee,
                    required_experience
                )
            )

            performance_score = (
                self.calculate_performance_score(
                    employee
                )
            )

            final_score = (
                self.calculate_final_score(
                    skill_match,
                    workload_score,
                    experience_score,
                    performance_score
                )
            )

            results.append({

                "employee_id":
                    employee.employee_id,

                "name":
                    employee.name,

                "skill_match":
                    round(skill_match, 2),

                "workload_score":
                    round(workload_score, 2),

                "experience_score":
                    round(experience_score, 2),

                "performance_score":
                    round(performance_score, 2),

                "final_score":
                    final_score
            })

        results.sort(
            key=lambda x: x["final_score"],
            reverse=True
        )

        return results[:top_k]

    # ---------------------------------------------------------
    # Calculate employee skill contribution
    # ---------------------------------------------------------

    def calculate_employee_skill_contribution(
        self,
        employee_id,
        required_skills,
        covered_skill_ids
    ):
        """
        Calculate how much an employee contributes
        to the currently selected team.
        """

        employee_skills = self.get_employee_skills(
            employee_id
        )

        contribution = 0.0
        matched_skills = []

        for required_skill in required_skills:

            skill_id = str(
                required_skill["skill_id"]
            )

            # Already covered by existing team
            if skill_id in covered_skill_ids:
                continue

            employee_skill = employee_skills.get(
                skill_id
            )

            if employee_skill is None:
                continue

            employee_level = float(
                employee_skill.get(
                    "level",
                    0
                )
            )

            required_level = float(
                required_skill.get(
                    "required_level",
                    0
                )
            )

            if employee_level >= required_level:

                # Critical skills get higher contribution
                if required_skill.get(
                    "is_critical",
                    False
                ):
                    contribution += 2.0
                else:
                    contribution += 1.0

                matched_skills.append(
                    skill_id
                )

        return contribution, matched_skills

    # ---------------------------------------------------------
    # BUILD TEAM FOR TASK
    # ---------------------------------------------------------

    def build_team_for_task(
        self,
        task_id,
        top_k=50
    ):

        from app.db.models import Task

        task = (
            self.db.query(Task)
            .filter(
                Task.task_id == task_id
            )
            .first()
        )

        if not task:
            return None

        required_skills = (
            self.get_task_required_skills(
                task_id
            )
        )

        required_team_size = int(
            task.team_size_required or 1
        )

        # Prevent unreasonable team size
        required_team_size = max(
            1,
            min(required_team_size, 20)
        )

        employees = (
            self.get_available_employees()
        )

        if not employees:

            return {
                "task_id": str(task_id),

                "required_team_size":
                    required_team_size,

                "team": [],

                "skill_coverage": 0.0,

                "covered_skills": [],

                "uncovered_skills": [
                    str(skill["skill_id"])
                    for skill in required_skills
                ],

                "uncovered_critical_skills": [
                    str(skill["skill_id"])
                    for skill in required_skills
                    if skill.get(
                        "is_critical",
                        False
                    )
                ],

                "team_valid": False,

                "recommendation_reason":
                    "No available employees found."
            }

        # ---------------------------------------------------------
        # STEP 1 — Calculate individual employee scores
        # ---------------------------------------------------------

        employee_scores = []

        for employee in employees:

            skill_match = (
                self.calculate_skill_match(
                    employee.employee_id,
                    required_skills
                )
            )

            workload_score = (
                self.calculate_workload_score(
                    employee
                )
            )

            experience_score = (
                self.calculate_experience_score(
                    employee,
                    task.required_experience_years or 0
                )
            )

            performance_score = (
                self.calculate_performance_score(
                    employee
                )
            )

            final_score = (
                self.calculate_final_score(
                    skill_match,
                    workload_score,
                    experience_score,
                    performance_score
                )
            )

            employee_scores.append({

                "employee": employee,

                "skill_match":
                    round(skill_match, 2),

                "workload_score":
                    round(workload_score, 2),

                "experience_score":
                    round(experience_score, 2),

                "performance_score":
                    round(performance_score, 2),

                "final_score":
                    final_score
            })

        # ---------------------------------------------------------
        # STEP 2 — Greedy team formation
        # ---------------------------------------------------------

        selected_team = []

        covered_skill_ids = set()

        remaining = employee_scores.copy()

        while (
            len(selected_team) < required_team_size
            and remaining
        ):

            best_candidate = None
            best_candidate_score = -1
            best_contribution = 0
            best_matched_skills = []

            for candidate in remaining:

                employee = candidate["employee"]

                contribution, matched_skills = (
                    self.calculate_employee_skill_contribution(
                        employee.employee_id,
                        required_skills,
                        covered_skill_ids
                    )
                )

                # Combine new skill contribution
                # with employee quality score.
                candidate_score = (
                    contribution * 60
                    +
                    candidate["final_score"] * 0.40
                )

                if candidate_score > best_candidate_score:

                    best_candidate = candidate

                    best_candidate_score = (
                        candidate_score
                    )

                    best_contribution = (
                        contribution
                    )

                    best_matched_skills = (
                        matched_skills
                    )

            if best_candidate is None:
                break

            employee = best_candidate["employee"]

            selected_team.append({

                "employee_id":
                    str(employee.employee_id),

                "name":
                    employee.name,

                "skill_match":
                    best_candidate["skill_match"],

                "workload_score":
                    best_candidate["workload_score"],

                "experience_score":
                    best_candidate["experience_score"],

                "performance_score":
                    best_candidate["performance_score"],

                "final_score":
                    best_candidate["final_score"],

                "contribution_score":
                    round(
                        best_contribution,
                        2
                    ),

                "matched_skills":
                    best_matched_skills
            })

            for skill_id in best_matched_skills:
                covered_skill_ids.add(
                    skill_id
                )

            remaining.remove(
                best_candidate
            )

            # Stop early when every required skill is covered
            if len(covered_skill_ids) >= len(
                required_skills
            ):
                break

        # ---------------------------------------------------------
        # STEP 3 — Calculate coverage
        # ---------------------------------------------------------

        all_required_skill_ids = {
            str(skill["skill_id"])
            for skill in required_skills
        }

        uncovered_skill_ids = (
            all_required_skill_ids
            -
            covered_skill_ids
        )

        critical_skill_ids = {
            str(skill["skill_id"])
            for skill in required_skills
            if skill.get(
                "is_critical",
                False
            )
        }

        uncovered_critical_skill_ids = (
            critical_skill_ids
            -
            covered_skill_ids
        )

        if all_required_skill_ids:

            skill_coverage = (
                len(covered_skill_ids)
                /
                len(all_required_skill_ids)
            ) * 100

        else:

            skill_coverage = 100.0

        # ---------------------------------------------------------
        # STEP 4 — Validation
        # ---------------------------------------------------------

        team_valid = (
            len(selected_team) == required_team_size
            and
            len(uncovered_critical_skill_ids) == 0
        )

        if team_valid:

            reason = (
                "Recommended team satisfies the required "
                "team size and covers all critical skills."
            )

        elif uncovered_critical_skill_ids:

            reason = (
                "Team size was formed, but some critical "
                "skills remain uncovered."
            )

        elif len(selected_team) < required_team_size:

            reason = (
                "Not enough available employees to form "
                "the requested team size."
            )

        else:

            reason = (
                "Team was formed but does not provide "
                "complete skill coverage."
            )

        return {

            "task_id":
                str(task_id),

            "required_team_size":
                required_team_size,

            "team":
                selected_team,

            "skill_coverage":
                round(
                    skill_coverage,
                    2
                ),

            "covered_skills":
                list(
                    covered_skill_ids
                ),

            "uncovered_skills":
                list(
                    uncovered_skill_ids
                ),

            "uncovered_critical_skills":
                list(
                    uncovered_critical_skill_ids
                ),

            "team_valid":
                team_valid,

            "recommendation_reason":
                reason
        }