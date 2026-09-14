"""
DEMO SEED
=========

Optional. Populates an empty database with a small, coherent dataset so
the UI has something to show and the model has something to score.

Safe to re-run: it skips any record that already exists, and it will not
touch a database that already has employees unless you pass --force.

    cd backend
    python -m app.etl.seed_demo

For the full research dataset use the existing loaders in app/etl
(load_all.py) against the CSVs in data/.
"""

import sys

from app.db.database import Base, SessionLocal, engine
from app.db.models import (
    Employee,
    EmployeeSkill,
    Project,
    Skill,
    Task,
    TaskSkill,
)


SKILLS = [
    ("SK_PY", "Python"),
    ("SK_SQL", "PostgreSQL"),
    ("SK_API", "REST API"),
    ("SK_DJ", "Django"),
    ("SK_DOC", "Docker"),
    ("SK_AWS", "AWS"),
    ("SK_SPARK", "Spark"),
    ("SK_REACT", "React"),
    ("SK_ETL", "ETL"),
    ("SK_SEC", "Security"),
]

EMPLOYEES = [
    # id, name, role, years, perf, workload, availability, critical_exp
    ("EMP001", "Sarah Johnson", "Backend Developer", 6.0, 91, 35, 80, 1),
    ("EMP002", "Michael Chen", "Backend Developer", 4.0, 84, 55, 70, 0),
    ("EMP003", "Emily Davis", "Data Engineer", 5.0, 88, 45, 65, 1),
    ("EMP004", "David Wilson", "Backend Developer", 2.0, 72, 20, 95, 0),
    ("EMP005", "Priya Nair", "Data Engineer", 7.0, 93, 60, 55, 1),
    ("EMP006", "James Okafor", "DevOps Engineer", 5.0, 86, 40, 75, 1),
    ("EMP007", "Lena Fischer", "Data Scientist", 8.0, 95, 70, 45, 1),
    ("EMP008", "Tomas Silva", "Cloud Engineer", 3.0, 78, 30, 85, 0),
]

EMPLOYEE_SKILLS = {
    "EMP001": [("SK_PY", 5), ("SK_DJ", 4), ("SK_API", 5), ("SK_SQL", 4)],
    "EMP002": [("SK_PY", 4), ("SK_API", 4), ("SK_DOC", 3)],
    "EMP003": [("SK_PY", 4), ("SK_SQL", 5), ("SK_ETL", 5), ("SK_SPARK", 4)],
    "EMP004": [("SK_PY", 3), ("SK_DJ", 3), ("SK_API", 3)],
    "EMP005": [("SK_PY", 5), ("SK_SPARK", 5), ("SK_ETL", 5), ("SK_AWS", 4)],
    "EMP006": [("SK_DOC", 5), ("SK_AWS", 5), ("SK_SEC", 4), ("SK_PY", 3)],
    "EMP007": [("SK_PY", 5), ("SK_SPARK", 4), ("SK_SQL", 4)],
    "EMP008": [("SK_AWS", 4), ("SK_DOC", 4), ("SK_SEC", 3)],
}

PROJECTS = [
    ("PRJ001", "FinTech", "API Development", "Moderate", "High", "High"),
    ("PRJ002", "Healthcare", "Data Engineering", "Advanced", "Critical",
     "Urgent"),
]

TASKS = [
    # id, project, title, complexity, criticality, role, size, hours,
    # deadline_days, priority, required_years
    ("TASK001", "PRJ001", "Build payment authentication API",
     "Moderate", "High", "Backend Developer", 2, 120, 30, "High", 3),
    ("TASK002", "PRJ001", "Integrate fraud scoring service",
     "Advanced", "High", "Backend Developer", 1, 80, 20, "Medium", 4),
    ("TASK003", "PRJ002", "Patient records ingestion pipeline",
     "Advanced", "Critical", "Data Engineer", 2, 160, 45, "Urgent", 4),
]

TASK_SKILLS = {
    "TASK001": [("SK_PY", 4, True), ("SK_API", 4, True), ("SK_DJ", 3, False)],
    "TASK002": [("SK_PY", 4, True), ("SK_API", 3, False),
                ("SK_SEC", 3, True)],
    "TASK003": [("SK_ETL", 4, True), ("SK_SPARK", 4, True),
                ("SK_SQL", 4, False)],
}


def seed(force: bool = False) -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        existing = db.query(Employee).count()

        if existing and not force:
            print(
                f"Database already has {existing} employees. "
                "Nothing to do (use --force to add the demo rows anyway)."
            )
            return

        def add_if_missing(model, pk_column, pk_value, instance):
            found = (
                db.query(model)
                .filter(pk_column == pk_value)
                .first()
            )
            if found is None:
                db.add(instance)
                return 1
            return 0

        counts = dict.fromkeys(
            ["skills", "employees", "employee_skills",
             "projects", "tasks", "task_skills"], 0
        )

        for skill_id, name in SKILLS:
            counts["skills"] += add_if_missing(
                Skill, Skill.skill_id, skill_id,
                Skill(skill_id=skill_id, skill_name=name),
            )
        db.flush()

        for (eid, name, role, years, perf, workload,
             availability, critical) in EMPLOYEES:
            counts["employees"] += add_if_missing(
                Employee, Employee.employee_id, eid,
                Employee(
                    employee_id=eid, name=name, role=role,
                    seniority="Senior" if years >= 5 else "Mid",
                    years_experience=years, performance_score=perf,
                    current_workload_pct=workload,
                    availability_pct=availability,
                    critical_project_experience=critical,
                ),
            )
        db.flush()

        for eid, rows in EMPLOYEE_SKILLS.items():
            for skill_id, level in rows:
                found = (
                    db.query(EmployeeSkill)
                    .filter(
                        EmployeeSkill.employee_id == eid,
                        EmployeeSkill.skill_id == skill_id,
                    )
                    .first()
                )
                if found is None:
                    db.add(EmployeeSkill(
                        employee_id=eid,
                        skill_id=skill_id,
                        skill_level=level,
                    ))
                    counts["employee_skills"] += 1
        db.flush()

        for pid, domain, ptype, complexity, criticality, priority in PROJECTS:
            counts["projects"] += add_if_missing(
                Project, Project.project_id, pid,
                Project(
                    project_id=pid, project_domain=domain,
                    project_type=ptype, project_complexity=complexity,
                    project_criticality=criticality, priority=priority,
                ),
            )
        db.flush()

        for (tid, pid, title, complexity, criticality, role, size,
             hours, deadline, priority, years) in TASKS:
            counts["tasks"] += add_if_missing(
                Task, Task.task_id, tid,
                Task(
                    task_id=tid, project_id=pid, task_title=title,
                    task_description=f"{title}.",
                    project_complexity=complexity,
                    project_criticality=criticality,
                    role_required=role, team_size_required=size,
                    estimated_hours=hours, deadline_days=deadline,
                    priority=priority, required_experience_years=years,
                    assigned_count=0,
                ),
            )
        db.flush()

        for tid, rows in TASK_SKILLS.items():
            for skill_id, level, critical in rows:
                found = (
                    db.query(TaskSkill)
                    .filter(
                        TaskSkill.task_id == tid,
                        TaskSkill.skill_id == skill_id,
                    )
                    .first()
                )
                if found is None:
                    db.add(TaskSkill(
                        task_id=tid, skill_id=skill_id,
                        required_level=level, is_critical=critical,
                    ))
                    counts["task_skills"] += 1

        db.commit()

        print("Seed complete:")
        for key, value in counts.items():
            print(f"  {key:18} +{value}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed(force="--force" in sys.argv)
