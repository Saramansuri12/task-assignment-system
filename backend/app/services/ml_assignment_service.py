"""
ML ASSIGNMENT SERVICE
=====================

Database -> Adapter -> Trained XGBoost pipeline -> Ranked employees

This is the layer the API calls. It does not re-train, re-implement or
replace the existing model; it only feeds it correctly shaped rows.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.db.models import (
    Assignment,
    Employee,
    EmployeeSkill,
    Project,
    Skill,
    Task,
    TaskSkill,
)

from app.ml.feature_adapter import (
    MODEL_FEATURE_COLUMNS,
    build_employee_payload,
    build_feature_row,
    build_task_payload,
    check_eligibility,
)


MODEL_PATH = (
    Path(__file__).resolve().parents[3]
    / "ml"
    / "models"
    / "xgboost_assignment_model.pkl"
)


class _ModelHolder:
    """Process-wide cache so the 1.3 MB pipeline loads once."""

    model = None
    loaded = False
    load_error: Optional[str] = None


def get_model():

    if _ModelHolder.loaded:
        return _ModelHolder.model

    _ModelHolder.loaded = True

    if not MODEL_PATH.exists():
        _ModelHolder.load_error = f"Model file not found: {MODEL_PATH}"
        print(f"[ML] {_ModelHolder.load_error}")
        return None

    try:
        import joblib

        _ModelHolder.model = joblib.load(MODEL_PATH)
        print(f"[ML] Loaded assignment model: {MODEL_PATH.name}")

    except Exception as exc:
        _ModelHolder.load_error = f"{type(exc).__name__}: {exc}"
        print(f"[ML] Could not load model - {_ModelHolder.load_error}")
        _ModelHolder.model = None

    return _ModelHolder.model


class MLAssignmentService:

    def __init__(self, db: Session):
        self.db = db
        self.model = get_model()

    # =================================================================
    # MODEL STATUS
    # =================================================================

    @property
    def model_available(self) -> bool:
        return self.model is not None

    @property
    def scoring_method(self) -> str:
        return "ml_model" if self.model_available else "rule_based_fallback"

    # =================================================================
    # DATA LOADING
    # =================================================================

    def _load_task_context(self, task_id: str):

        task = (
            self.db.query(Task)
            .filter(Task.task_id == task_id)
            .first()
        )

        if task is None:
            return None, None, []

        project = (
            self.db.query(Project)
            .filter(Project.project_id == task.project_id)
            .first()
        )

        task_skill_rows = (
            self.db.query(TaskSkill, Skill)
            .outerjoin(Skill, TaskSkill.skill_id == Skill.skill_id)
            .filter(TaskSkill.task_id == task_id)
            .all()
        )

        return task, project, task_skill_rows

    def _load_candidate_employees(self) -> List[Employee]:
        """
        Availability/workload gating is intentionally lenient here.
        The eligibility rules from ml/matching/eligibility.py do the
        real filtering, so the API can also report WHY someone was
        rejected instead of silently dropping them.
        """

        return self.db.query(Employee).all()

    def _load_skills_by_employee(self) -> Dict[str, List[Any]]:

        rows = (
            self.db.query(EmployeeSkill, Skill)
            .outerjoin(Skill, EmployeeSkill.skill_id == Skill.skill_id)
            .all()
        )

        grouped: Dict[str, List[Any]] = {}

        for employee_skill, skill in rows:
            grouped.setdefault(
                str(employee_skill.employee_id), []
            ).append((employee_skill, skill))

        return grouped

    def _load_domains_by_employee(self) -> Dict[str, List[str]]:
        """
        The Employee table has no `domains` column, so derive it from
        work history: assignments -> tasks -> projects -> domain.
        """

        rows = (
            self.db.query(Assignment.employee_id, Project.project_domain)
            .join(Task, Assignment.task_id == Task.task_id)
            .join(Project, Task.project_id == Project.project_id)
            .filter(Project.project_domain.isnot(None))
            .distinct()
            .all()
        )

        grouped: Dict[str, List[str]] = {}

        for employee_id, domain in rows:
            grouped.setdefault(str(employee_id), []).append(domain)

        return grouped

    # =================================================================
    # PREDICTION
    # =================================================================

    def _predict_batch(self, feature_rows: List[Dict[str, Any]]) -> List[float]:
        """
        One vectorised call for all candidates rather than one call per
        employee. Returns success probability as a 0-100 percentage.
        """

        if not feature_rows:
            return []

        if not self.model_available:
            return [None] * len(feature_rows)

        try:
            import pandas as pd

            frame = pd.DataFrame(
                feature_rows,
                columns=MODEL_FEATURE_COLUMNS,
            )

            probabilities = self.model.predict_proba(frame)[:, 1]

            return [
                round(float(value) * 100, 2)
                for value in probabilities
            ]

        except Exception as exc:
            print(f"[ML] Batch prediction failed: {exc}")
            return [None] * len(feature_rows)

    # =================================================================
    # RULE-BASED FALLBACK SCORE
    # =================================================================

    @staticmethod
    def _fallback_score(row: Dict[str, Any]) -> float:

        def number(value, default=0.0):
            try:
                return float(value)
            except (TypeError, ValueError):
                return default

        score = (
            number(row.get("skill_match_pct")) * 0.35
            + number(row.get("critical_skill_match_pct")) * 0.20
            + number(row.get("experience_match_pct")) * 0.15
            + number(row.get("performance_score"), 50.0) * 0.20
            + (100 - number(row.get("current_workload_pct"))) * 0.10
        )

        return round(max(0.0, min(score, 100.0)), 2)

    # =================================================================
    # RANK EMPLOYEES FOR A TASK
    # =================================================================

    def rank_employees_for_task(
        self,
        task_id: str,
        top_k: int = 10,
        include_ineligible: bool = False,
    ) -> Optional[Dict[str, Any]]:

        task, project, task_skill_rows = self._load_task_context(task_id)

        if task is None:
            return None

        task_payload = build_task_payload(
            task,
            project,
            task_skill_rows,
        )

        employees = self._load_candidate_employees()
        skills_by_employee = self._load_skills_by_employee()
        domains_by_employee = self._load_domains_by_employee()

        feature_rows = []
        staged = []

        for employee in employees:

            employee_key = str(employee.employee_id)

            employee_payload = build_employee_payload(
                employee,
                skills_by_employee.get(employee_key, []),
                domains_by_employee.get(employee_key, []),
            )

            row, matching = build_feature_row(
                employee_payload,
                task_payload,
            )

            eligibility = check_eligibility(
                employee_payload,
                task_payload,
                matching,
            )

            feature_rows.append(row)

            staged.append({
                "employee": employee,
                "payload": employee_payload,
                "row": row,
                "matching": matching,
                "eligibility": eligibility,
            })

        probabilities = self._predict_batch(feature_rows)

        eligible: List[Dict[str, Any]] = []
        rejected: List[Dict[str, Any]] = []

        for item, probability in zip(staged, probabilities):

            employee = item["employee"]
            matching = item["matching"]
            row = item["row"]

            if probability is None:
                score = self._fallback_score(row)
                method = "rule_based_fallback"
            else:
                score = probability
                method = "ml_model"

            record = {
                "employee_id": str(employee.employee_id),
                "name": employee.name,
                "employee_name": employee.name,
                "role": employee.role,

                "score": score,
                "success_probability": score,
                "match_score": score,
                "final_score": score,
                "scoring_method": method,

                "skill_match": matching["skill_match_pct"],
                "skill_match_pct": matching["skill_match_pct"],
                "critical_skill_match_pct":
                    matching["critical_skill_match_pct"],
                "skill_level_match_pct":
                    matching["skill_level_match_pct"],
                "experience_match": matching["experience_match_pct"],
                "experience_match_pct": matching["experience_match_pct"],
                "domain_match": matching["domain_match"],
                "role_match": matching["role_match"],

                "current_workload_pct": employee.current_workload_pct,
                "availability_pct": employee.availability_pct,
                "availability_score": employee.availability_pct or 0,
                "performance_score": employee.performance_score,
                "reliability_score": employee.performance_score,

                "reason": self._build_reason(
                    employee,
                    matching,
                    score,
                    method,
                ),
            }

            if item["eligibility"]["eligible"]:
                eligible.append(record)
            else:
                record["rejection_reasons"] = item["eligibility"]["reasons"]
                rejected.append(record)

        eligible.sort(key=lambda item: item["score"], reverse=True)

        for index, record in enumerate(eligible, start=1):
            record["rank"] = index

        recommendations = eligible[:top_k]

        # If nothing clears the eligibility bar, fall back to the best
        # near-misses so the UI is never empty with no explanation.
        used_fallback_pool = False

        if not recommendations and rejected:
            rejected.sort(key=lambda item: item["score"], reverse=True)
            recommendations = rejected[:top_k]
            used_fallback_pool = True

            for index, record in enumerate(recommendations, start=1):
                record["rank"] = index

        return {
            "task_id": str(task_id),
            "project_id": str(task.project_id),

            "model_available": self.model_available,
            "scoring_method": self.scoring_method,
            "model_error": _ModelHolder.load_error,

            "required_skills": task_payload["required_skills"],
            "critical_skills": task_payload["critical_skills"],
            "required_experience_years":
                task_payload["required_experience"],

            "total_candidates": len(employees),
            "eligible_candidates": len(eligible),
            "showing_near_misses": used_fallback_pool,

            "recommendations": recommendations,
            "rejected_employees": [
                {
                    "employee_id": record["employee_id"],
                    "name": record["name"],
                    "score": record["score"],
                    "reasons": record["rejection_reasons"],
                }
                for record in rejected[:20]
            ],
        }

    # =================================================================
    # BUILD TEAM
    # =================================================================

    def build_team_for_task(
        self,
        task_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Greedy team formation driven by ML score + marginal skill
        coverage. Reuses rank_employees_for_task so the team is built
        on model probabilities, not a separate heuristic.
        """

        task, project, task_skill_rows = self._load_task_context(task_id)

        if task is None:
            return None

        ranking = self.rank_employees_for_task(
            task_id,
            top_k=200,
            include_ineligible=True,
        )

        required_team_size = max(1, min(int(task.team_size_required or 1), 20))

        # skill name -> (required_level, is_critical)
        requirements = {}

        for task_skill, skill in task_skill_rows:
            name = (
                skill.skill_name
                if skill is not None and skill.skill_name
                else str(task_skill.skill_id)
            )
            requirements[name] = (
                float(task_skill.required_level or 0),
                bool(task_skill.is_critical),
            )

        skills_by_employee = self._load_skills_by_employee()

        def employee_skill_map(employee_id: str) -> Dict[str, float]:
            result = {}
            for employee_skill, skill in skills_by_employee.get(
                str(employee_id), []
            ):
                name = (
                    skill.skill_name
                    if skill is not None and skill.skill_name
                    else str(employee_skill.skill_id)
                )
                result[name] = float(employee_skill.skill_level or 0)
            return result

        candidates = list(ranking["recommendations"])

        if not candidates:
            return {
                "task_id": str(task_id),
                "required_team_size": required_team_size,
                "team": [],
                "skill_coverage": 0.0,
                "covered_skills": [],
                "uncovered_skills": list(requirements.keys()),
                "uncovered_critical_skills": [
                    name
                    for name, (_, critical) in requirements.items()
                    if critical
                ],
                "team_valid": False,
                "scoring_method": self.scoring_method,
                "model_available": self.model_available,
                "recommendation_reason":
                    "No available employees matched this task.",
            }

        team = []
        covered = set()
        remaining = candidates.copy()

        while len(team) < required_team_size and remaining:

            best = None
            best_value = -1.0
            best_contribution = 0.0
            best_matched = []

            for candidate in remaining:

                owned = employee_skill_map(candidate["employee_id"])

                contribution = 0.0
                matched = []

                for name, (level, critical) in requirements.items():

                    if name in covered:
                        continue

                    if owned.get(name, 0) >= level:
                        contribution += 2.0 if critical else 1.0
                        matched.append(name)

                value = contribution * 60 + candidate["score"] * 0.4

                if value > best_value:
                    best = candidate
                    best_value = value
                    best_contribution = contribution
                    best_matched = matched

            if best is None:
                break

            team.append({
                **best,
                "contribution_score": round(best_contribution, 2),
                "matched_skills": best_matched,
            })

            covered.update(best_matched)
            remaining.remove(best)

        all_required = set(requirements.keys())
        critical_required = {
            name for name, (_, critical) in requirements.items() if critical
        }

        uncovered = all_required - covered
        uncovered_critical = critical_required - covered

        coverage = (
            round(len(covered) / len(all_required) * 100, 2)
            if all_required
            else 100.0
        )

        team_valid = (
            len(team) == required_team_size
            and not uncovered_critical
        )

        if team_valid:
            reason = (
                "Recommended team meets the required size and covers "
                "every critical skill."
            )
        elif uncovered_critical:
            reason = (
                "Team was formed but these critical skills are still "
                "uncovered: " + ", ".join(sorted(uncovered_critical))
            )
        elif len(team) < required_team_size:
            reason = (
                "Only "
                f"{len(team)} of {required_team_size} required members "
                "could be sourced from eligible employees."
            )
        else:
            reason = "Team formed with partial skill coverage."

        return {
            "task_id": str(task_id),
            "required_team_size": required_team_size,
            "team": team,

            "skill_coverage": coverage,
            "covered_skills": sorted(covered),
            "uncovered_skills": sorted(uncovered),
            "uncovered_critical_skills": sorted(uncovered_critical),

            "team_valid": team_valid,
            "scoring_method": self.scoring_method,
            "model_available": self.model_available,
            "recommendation_reason": reason,
        }

    # =================================================================
    # SINGLE PAIR SCORE (used when an assignment is created)
    # =================================================================

    def score_pair(
        self,
        task_id: str,
        employee_id: str,
    ) -> Optional[float]:
        """Success probability 0-1 for one employee on one task."""

        task, project, task_skill_rows = self._load_task_context(task_id)

        if task is None:
            return None

        employee = (
            self.db.query(Employee)
            .filter(Employee.employee_id == employee_id)
            .first()
        )

        if employee is None:
            return None

        employee_skill_rows = (
            self.db.query(EmployeeSkill, Skill)
            .outerjoin(Skill, EmployeeSkill.skill_id == Skill.skill_id)
            .filter(EmployeeSkill.employee_id == employee_id)
            .all()
        )

        domains = self._load_domains_by_employee().get(
            str(employee_id), []
        )

        row, _ = build_feature_row(
            build_employee_payload(
                employee,
                employee_skill_rows,
                domains,
            ),
            build_task_payload(task, project, task_skill_rows),
        )

        scores = self._predict_batch([row])

        if not scores or scores[0] is None:
            return round(self._fallback_score(row) / 100, 4)

        return round(scores[0] / 100, 4)

    # =================================================================
    # REASON TEXT
    # =================================================================

    @staticmethod
    def _build_reason(employee, matching, score, method) -> str:

        parts = []

        if method == "ml_model":
            parts.append(
                f"Model predicts a {score}% chance of successful delivery"
            )
        else:
            parts.append(f"Weighted match score of {score}%")

        parts.append(
            f"{matching['skill_match_pct']}% of required skills covered"
        )

        if matching["critical_skill_match_pct"] >= 100:
            parts.append("all critical skills held")
        elif matching["critical_skill_match_pct"] > 0:
            parts.append(
                f"{matching['critical_skill_match_pct']}% of critical "
                "skills held"
            )

        if matching["role_match"]:
            parts.append(f"role matches ({employee.role})")

        if matching["domain_match"]:
            parts.append("has prior experience in this project domain")

        if employee.current_workload_pct is not None:
            parts.append(
                f"currently at {employee.current_workload_pct}% workload"
            )

        return "; ".join(parts) + "."
