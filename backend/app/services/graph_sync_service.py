from sqlalchemy.orm import Session

from app.db.models import (
    Employee,
    Skill,
    EmployeeSkill,
    Task,
    TaskSkill,
)

from app.services.neo4j_service import Neo4jService


class GraphSyncService:

    def __init__(self, db: Session):

        self.db = db
        self.graph = Neo4jService()

    # =====================================================
    # SYNC SKILLS
    # =====================================================

    def sync_skills(self):

        skills = (
            self.db.query(Skill)
            .all()
        )

        count = 0

        for skill in skills:

            self.graph.create_skill(
                skill_id=skill.skill_id,
                skill_name=skill.skill_name
            )

            count += 1

        return count

    # =====================================================
    # SYNC EMPLOYEES
    # =====================================================

    def sync_employees(self):

        employees = (
            self.db.query(Employee)
            .all()
        )

        count = 0

        for employee in employees:

            self.graph.create_employee(
                employee_id=employee.employee_id,
                name=employee.name
            )

            count += 1

        return count

    # =====================================================
    # SYNC EMPLOYEE SKILLS
    # =====================================================

    def sync_employee_skills(self):

        employee_skills = (
            self.db.query(EmployeeSkill)
            .all()
        )

        count = 0

        for record in employee_skills:

            self.graph.connect_employee_skill(
                employee_id=record.employee_id,
                skill_id=record.skill_id,
                skill_level=record.skill_level
            )

            count += 1

        return count

    # =====================================================
    # SYNC TASK SKILLS
    # =====================================================

    def sync_task_skills(self):

        task_skills = (
            self.db.query(TaskSkill)
            .all()
        )

        count = 0

        for record in task_skills:

            self.graph.connect_task_skill(
                task_id=record.task_id,
                skill_id=record.skill_id,
                required_level=record.required_level
            )

            count += 1

        return count

    # =====================================================
    # FULL SYNC
    # =====================================================

    def sync_all(self):

        print("=" * 70)
        print("NEO4J GRAPH SYNCHRONIZATION")
        print("=" * 70)

        print("\nSTEP 1 - Skills")
        skills = self.sync_skills()
        print(f"Synced: {skills}")

        print("\nSTEP 2 - Employees")
        employees = self.sync_employees()
        print(f"Synced: {employees}")

        print("\nSTEP 3 - Employee Skills")
        employee_skills = self.sync_employee_skills()
        print(f"Synced: {employee_skills}")

        print("\nSTEP 4 - Task Skills")
        task_skills = self.sync_task_skills()
        print(f"Synced: {task_skills}")

        print("\n" + "=" * 70)
        print("NEO4J SYNCHRONIZATION COMPLETE")
        print("=" * 70)

        return {
            "skills": skills,
            "employees": employees,
            "employee_skills": employee_skills,
            "task_skills": task_skills,
        }