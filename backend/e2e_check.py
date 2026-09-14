"""End-to-end API check. Run with: python e2e_check.py"""
import os
import sys

os.environ.setdefault("DATABASE_URL", "sqlite:///./dev_local.db")

import httpx
from app.db.database import SessionLocal
from app.db.models import (
    Employee, Skill, EmployeeSkill, Project, Task, TaskSkill, Assignment,
)

BASE = os.environ.get("E2E_BASE", "http://127.0.0.1:8010")
client = httpx.Client(base_url=BASE, timeout=60.0)

OK, FAIL = [], []


def check(label, method, path, expect=(200, 201), **kw):
    try:
        r = client.request(method, path, **kw)
    except Exception as exc:
        FAIL.append(f"{label}: EXCEPTION {type(exc).__name__}: {exc}")
        return None
    if r.status_code in expect:
        OK.append(f"{label}: {r.status_code}")
        try:
            return r.json()
        except Exception:
            return r.text
    body = r.text[:300]
    FAIL.append(f"{label}: {method} {path} -> {r.status_code} {body}")
    try:
        return r.json()
    except Exception:
        return None


def seed():
    db = SessionLocal()
    if db.query(Employee).count():
        db.close()
        return
    skills = [
        ("SK_PY", "Python"), ("SK_DJ", "Django"), ("SK_API", "REST API"),
        ("SK_SQL", "PostgreSQL"), ("SK_DOC", "Docker"),
    ]
    for sid, sname in skills:
        db.add(Skill(skill_id=sid, skill_name=sname))

    emps = [
        ("EMP001", "Sarah Johnson", "Backend Developer", 6.0, 91.0, 35.0, 80.0, 1),
        ("EMP002", "Michael Chen", "Backend Developer", 4.0, 84.0, 55.0, 70.0, 0),
        ("EMP003", "Emily Davis", "Data Engineer", 5.0, 88.0, 45.0, 60.0, 1),
        ("EMP004", "David Wilson", "Backend Developer", 2.0, 72.0, 20.0, 95.0, 0),
    ]
    for eid, name, role, yrs, perf, wl, av, cpe in emps:
        db.add(Employee(
            employee_id=eid, name=name, role=role, seniority="Mid",
            years_experience=yrs, performance_score=perf,
            current_workload_pct=wl, availability_pct=av,
            critical_project_experience=cpe,
        ))
    db.flush()

    grants = {
        "EMP001": [("SK_PY", 5), ("SK_DJ", 4), ("SK_API", 5), ("SK_SQL", 4)],
        "EMP002": [("SK_PY", 4), ("SK_API", 4), ("SK_DOC", 3)],
        "EMP003": [("SK_PY", 3), ("SK_SQL", 5)],
        "EMP004": [("SK_PY", 3), ("SK_DJ", 3), ("SK_API", 3)],
    }
    for eid, rows in grants.items():
        for sid, lvl in rows:
            db.add(EmployeeSkill(employee_id=eid, skill_id=sid, skill_level=lvl))

    db.add(Project(
        project_id="PRJ001", project_domain="FinTech",
        project_type="API Development", project_complexity="Moderate",
        project_criticality="High", priority="High",
    ))
    db.flush()
    db.add(Task(
        task_id="TASK001", project_id="PRJ001",
        task_title="Build payment authentication API",
        task_description="Secure auth endpoints",
        project_complexity="Moderate", project_criticality="High",
        role_required="Backend Developer", team_size_required=2,
        estimated_hours=120, deadline_days=30, priority="High",
        required_experience_years=3,
    ))
    db.flush()
    for sid, lvl, crit in [("SK_PY", 4, True), ("SK_API", 4, True), ("SK_DJ", 3, False)]:
        db.add(TaskSkill(task_id="TASK001", skill_id=sid,
                         required_level=lvl, is_critical=crit))
    db.commit()
    db.close()


def main():
    seed()
    print("=" * 70)

    check("root", "GET", "/")
    check("health", "GET", "/health")

    check("register", "POST", "/auth/register", expect=(201, 409), json={
        "username": "manager1", "email": "m1@example.com",
        "password": "password123", "role": "MANAGER"})
    tok = check("login", "POST", "/auth/login",
                json={"username": "manager1", "password": "password123"})
    if tok and tok.get("access_token"):
        client.headers["Authorization"] = f"Bearer {tok['access_token']}"
    check("auth/me", "GET", "/auth/me")

    check("dashboard", "GET", "/dashboard/summary")
    check("employees list", "GET", "/employees/")
    check("employee detail", "GET", "/employees/EMP001")
    check("employee skills", "GET", "/employee-skills/employee/EMP001")
    check("skills list", "GET", "/skills/")

    check("projects list", "GET", "/projects/")
    check("project detail", "GET", "/projects/PRJ001")
    check("create project", "POST", "/projects/", json={
        "project_id": "PRJ_NEW_1", "project_domain": "Retail",
        "project_type": "Dashboards", "project_complexity": "Basic",
        "project_criticality": "Low", "priority": "Medium"})

    check("tasks list (no slash)", "GET", "/tasks")
    check("tasks list (slash)", "GET", "/tasks/")
    check("task detail", "GET", "/tasks/TASK001")
    check("task skills", "GET", "/task-skills/task/TASK001")
    check("create task", "POST", "/tasks", expect=(201,), json={
        "project_id": "PRJ001", "task_title": "New smoke task",
        "task_description": "created by smoke test",
        "project_complexity": "Basic", "project_criticality": "Low",
        "role_required": "Backend Developer", "team_size_required": 1,
        "estimated_hours": 20, "deadline_days": 10, "priority": "Medium",
        "required_experience_years": 1})

    rec = check("recommend", "GET", "/assignments/task/TASK001/recommend?top_k=5")
    if isinstance(rec, dict):
        print("   recommendation sample:", str(rec.get("recommendations", [])[:1])[:400])
    check("recommend-team", "GET", "/assignments/task/TASK001/recommend-team")
    check("recommendations router", "GET", "/recommendations/TASK001?top_k=3")
    check("validate", "GET", "/assignments/validate/TASK001/EMP001")
    check("workload", "GET", "/workload/employee/EMP001")

    check("create assignment", "POST", "/assignments", expect=(201,),
          json={"task_id": "TASK001", "employee_id": "EMP001"})
    alist = check("assignments list", "GET", "/assignments")
    check("task assignments", "GET", "/assignments/task/TASK001")
    check("employee assignments", "GET", "/assignments/employee/EMP001")

    aid = None
    if isinstance(alist, list) and alist:
        aid = alist[0].get("assignment_id")
    if aid:
        check("assignment detail", "GET", f"/assignments/{aid}")
        check("assignment history", "GET", f"/assignments/{aid}/history")
        check("update status", "PUT", f"/assignments/{aid}/status",
              json={"status": "IN_PROGRESS"})
        check("complete", "POST", f"/assignments/{aid}/complete", expect=(200, 409))
    else:
        FAIL.append("assignment id: could not obtain assignment_id from list")

    check("dashboard after", "GET", "/dashboard/summary")

    print("\nPASSED (%d):" % len(OK))
    for line in OK:
        print("  OK  ", line)
    print("\nFAILED (%d):" % len(FAIL))
    for line in FAIL:
        print("  X   ", line)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
