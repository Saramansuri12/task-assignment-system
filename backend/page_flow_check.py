"""
Replays the exact request sequence each frontend page makes, using the
browser's Origin header so CORS is exercised too.

Run the backend on :8010 first, then: python page_flow_check.py
"""
import json
import sys

import httpx

BASE = "http://127.0.0.1:8010"
ORIGIN = "http://localhost:5173"

client = httpx.Client(base_url=BASE, timeout=60.0, headers={"Origin": ORIGIN})

RESULTS = []


def preflight(method, path):
    """Simulate the browser's OPTIONS preflight."""
    r = client.request(
        "OPTIONS",
        path,
        headers={
            "Access-Control-Request-Method": method,
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    allow = r.headers.get("access-control-allow-origin")
    return r.status_code, allow


def call(page, label, method, path, expect=(200, 201), **kw):
    if method in ("POST", "PUT", "DELETE"):
        status, allow = preflight(method, path)
        if status not in (200, 204) or allow != ORIGIN:
            RESULTS.append(
                (page, label, False,
                 f"CORS preflight failed: {status} allow-origin={allow}")
            )
            return None

    r = client.request(method, path, **kw)

    allow = r.headers.get("access-control-allow-origin")

    if r.status_code in (301, 302, 307, 308):
        RESULTS.append(
            (page, label, False,
             f"REDIRECT {r.status_code} -> breaks browser CORS")
        )
        return None

    if allow != ORIGIN:
        RESULTS.append(
            (page, label, False,
             f"missing/!= CORS header: {allow!r}")
        )
        return None

    if r.status_code not in expect:
        RESULTS.append(
            (page, label, False, f"{r.status_code} {r.text[:160]}")
        )
        return None

    RESULTS.append((page, label, True, str(r.status_code)))

    try:
        return r.json()
    except Exception:
        return None


def main():
    # ---------- Login page ----------
    call("Login", "register", "POST", "/auth/register", expect=(201, 409),
         json={"username": "flowmgr", "email": "flow@example.com",
               "password": "password123", "role": "MANAGER"})

    token = call("Login", "login", "POST", "/auth/login",
                 json={"username": "flowmgr", "password": "password123"})

    if not token:
        print("Login failed - aborting")
        return 1

    client.headers["Authorization"] = f"Bearer {token['access_token']}"

    # ---------- Sidebar ----------
    call("Sidebar", "getCurrentUser", "GET", "/auth/me")

    # ---------- Dashboard ----------
    summary = call("Dashboard", "getDashboardSummary", "GET",
                   "/dashboard/summary")
    projects = call("Dashboard", "getProjects", "GET", "/projects/")
    tasks = call("Dashboard", "getTasks", "GET", "/tasks")
    assignments = call("Dashboard", "getAssignments", "GET", "/assignments")

    # Verify the shape Dashboard.jsx destructures
    if summary:
        for key in ("projects", "employees", "tasks", "assignments",
                    "success_rate"):
            ok = key in summary
            RESULTS.append(("Dashboard", f"summary.{key}", ok,
                            "present" if ok else "MISSING"))
        for key in ("total", "active", "completed", "successful"):
            ok = key in summary["assignments"]
            RESULTS.append(("Dashboard", f"summary.assignments.{key}", ok,
                            "present" if ok else "MISSING"))

    # ---------- Team page ----------
    employees = call("TeamManagement", "getEmployees", "GET", "/employees/")
    call("TeamManagement", "getSkills", "GET", "/skills/")

    employee_id = employees[0]["employee_id"] if employees else None

    if employee_id:
        call("TeamManagement", "getEmployeeSkills", "GET",
             f"/employee-skills/employee/{employee_id}")

        # ---------- Employee details ----------
        call("EmployeeDetails", "getEmployee", "GET",
             f"/employees/{employee_id}")
        call("EmployeeDetails", "getEmployeeAssignments", "GET",
             f"/assignments/employee/{employee_id}")
        call("EmployeeDetails", "getEmployeeWorkload", "GET",
             f"/workload/employee/{employee_id}")

    # ---------- Create project ----------
    project = call("CreateProject", "createProject", "POST", "/projects/",
                   expect=(201,),
                   json={"project_domain": "Healthcare",
                         "project_type": "Data Analytics",
                         "project_complexity": "Advanced",
                         "project_criticality": "High",
                         "priority": "High"})

    project_id = project["project_id"] if project else (
        projects[0]["project_id"] if projects else None)

    # ---------- Project details ----------
    if project_id:
        call("ProjectDetails", "getProject", "GET",
             f"/projects/{project_id}")

    # ---------- Create task with skills ----------
    task = call("CreateTask", "createTask", "POST", "/tasks", expect=(201,),
                json={"project_id": project_id,
                      "task_title": "Patient data pipeline",
                      "task_description": "Build ingestion pipeline",
                      "project_complexity": "Advanced",
                      "project_criticality": "High",
                      "priority": "High",
                      "role_required": "Data Engineer",
                      "team_size_required": 2,
                      "estimated_hours": 90,
                      "deadline_days": 21,
                      "required_experience_years": 3,
                      "required_skills": [
                          {"skill_name": "Python", "required_level": 3,
                           "is_critical": True},
                          {"skill_name": "PostgreSQL", "required_level": 3,
                           "is_critical": False},
                      ]})

    task_id = task["task_id"] if task else (
        tasks[0]["task_id"] if tasks else None)

    # Confirm the skills actually persisted
    if task_id:
        skills = call("CreateTask", "task skills persisted", "GET",
                      f"/task-skills/task/{task_id}")
        ok = bool(skills)
        RESULTS.append(("CreateTask", "required_skills saved", ok,
                        f"{len(skills or [])} rows"))

    # ---------- Requirements review ----------
    if project_id:
        call("RequirementsReview", "getProject", "GET",
             f"/projects/{project_id}")

    # ---------- Task details ----------
    if task_id:
        call("TaskDetails", "getTask", "GET", f"/tasks/{task_id}")
        call("TaskDetails", "getTaskSkills", "GET",
             f"/task-skills/task/{task_id}")
        call("TaskDetails", "getTaskAssignments", "GET",
             f"/assignments/task/{task_id}")

        rec = call("TaskDetails", "getAssignmentRecommendations", "GET",
                   f"/assignments/task/{task_id}/recommend?top_k=10")

        if rec:
            for key in ("recommendations", "scoring_method",
                        "total_candidates", "eligible_candidates",
                        "rejected_employees"):
                ok = key in rec
                RESULTS.append(("TaskDetails", f"recommend.{key}", ok,
                                "present" if ok else "MISSING"))

            if rec.get("recommendations"):
                member = rec["recommendations"][0]
                for key in ("employee_id", "name", "score", "reason",
                            "skill_match_pct", "critical_skill_match_pct",
                            "current_workload_pct", "role"):
                    ok = key in member
                    RESULTS.append(("TaskDetails", f"candidate.{key}", ok,
                                    "present" if ok else "MISSING"))

                # ---------- Assign the top candidate ----------
                top = member["employee_id"]
                created = call("TaskDetails", "createAssignment", "POST",
                               "/assignments", expect=(201, 409),
                               json={"task_id": task_id,
                                     "employee_id": top})

                if created and created.get("assignment_id"):
                    aid = created["assignment_id"]
                    call("Assignments", "updateAssignmentStatus", "PUT",
                         f"/assignments/{aid}/status",
                         json={"status": "IN_PROGRESS"})
                    call("Assignments", "getAssignmentHistory", "GET",
                         f"/assignments/{aid}/history")

        # ---------- Team recommendation ----------
        team = call("TeamRecommendation", "getTeamRecommendation", "GET",
                    f"/assignments/task/{task_id}/recommend-team")

        if team:
            for key in ("team", "skill_coverage", "covered_skills",
                        "uncovered_skills", "uncovered_critical_skills",
                        "team_valid", "recommendation_reason",
                        "required_team_size"):
                ok = key in team
                RESULTS.append(("TeamRecommendation", f"team.{key}", ok,
                                "present" if ok else "MISSING"))

    # ---------- Dashboard reflects the new work ----------
    after = call("Dashboard", "summary after mutations", "GET",
                 "/dashboard/summary")

    if summary and after:
        grew = after["assignments"]["total"] >= summary["assignments"]["total"]
        RESULTS.append(("Dashboard", "stats update after assignment", grew,
                        f"{summary['assignments']['total']} -> "
                        f"{after['assignments']['total']}"))

    # ---------- report ----------
    passed = [r for r in RESULTS if r[2]]
    failed = [r for r in RESULTS if not r[2]]

    current = None
    for page, label, ok, note in RESULTS:
        if page != current:
            print(f"\n--- {page} ---")
            current = page
        print(f"  {'OK ' if ok else 'FAIL'}  {label:<38} {note}")

    print(f"\n{len(passed)} passed, {len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
