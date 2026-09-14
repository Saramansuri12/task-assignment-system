from app.db.neo4j import neo4j_connection


class Neo4jService:

    # =========================================================
    # CREATE CONSTRAINTS / INDEXES
    # =========================================================

    def create_constraints(self):

        queries = [
            """
            CREATE CONSTRAINT employee_id_unique IF NOT EXISTS
            FOR (e:Employee)
            REQUIRE e.employee_id IS UNIQUE
            """,

            """
            CREATE CONSTRAINT skill_id_unique IF NOT EXISTS
            FOR (s:Skill)
            REQUIRE s.skill_id IS UNIQUE
            """,

            """
            CREATE CONSTRAINT task_id_unique IF NOT EXISTS
            FOR (t:Task)
            REQUIRE t.task_id IS UNIQUE
            """
        ]

        with neo4j_connection.driver.session() as session:

            for query in queries:
                session.run(query).consume()

    # =========================================================
    # CREATE EMPLOYEE
    # =========================================================

    def create_employee(
        self,
        employee_id,
        name
    ):

        query = """
        MERGE (e:Employee {
            employee_id: $employee_id
        })

        SET e.name = $name

        RETURN e
        """

        with neo4j_connection.driver.session() as session:

            result = session.run(
                query,
                employee_id=str(employee_id),
                name=name
            )

            return result.single()

    # =========================================================
    # CREATE SKILL
    # =========================================================

    def create_skill(
        self,
        skill_id,
        skill_name
    ):

        query = """
        MERGE (s:Skill {
            skill_id: $skill_id
        })

        SET s.name = $skill_name

        RETURN s
        """

        with neo4j_connection.driver.session() as session:

            result = session.run(
                query,
                skill_id=str(skill_id),
                skill_name=skill_name
            )

            return result.single()

    # =========================================================
    # BATCH CREATE EMPLOYEES
    # =========================================================

    def create_employees_batch(self, employees):

        query = """
        UNWIND $employees AS row

        MERGE (e:Employee {
            employee_id: row.employee_id
        })

        SET e.name = row.name
        """

        with neo4j_connection.driver.session() as session:

            session.run(
                query,
                employees=employees
            ).consume()

    # =========================================================
    # BATCH CREATE SKILLS
    # =========================================================

    def create_skills_batch(self, skills):

        query = """
        UNWIND $skills AS row

        MERGE (s:Skill {
            skill_id: row.skill_id
        })

        SET s.name = row.name
        """

        with neo4j_connection.driver.session() as session:

            session.run(
                query,
                skills=skills
            ).consume()

    # =========================================================
    # EMPLOYEE HAS SKILL
    # =========================================================

    def connect_employee_skill(
        self,
        employee_id,
        skill_id,
        skill_level
    ):

        query = """
        MATCH (e:Employee {
            employee_id: $employee_id
        })

        MATCH (s:Skill {
            skill_id: $skill_id
        })

        MERGE (e)-[r:HAS_SKILL]->(s)

        SET r.level = $skill_level

        RETURN e, s, r
        """

        with neo4j_connection.driver.session() as session:

            result = session.run(
                query,
                employee_id=str(employee_id),
                skill_id=str(skill_id),
                skill_level=float(skill_level)
            )

            return result.single()

    # =========================================================
    # BATCH EMPLOYEE -> SKILL
    # =========================================================

    def create_employee_skills_batch(
        self,
        employee_skills
    ):

        query = """
        UNWIND $records AS row

        MATCH (e:Employee {
            employee_id: row.employee_id
        })

        MATCH (s:Skill {
            skill_id: row.skill_id
        })

        MERGE (e)-[r:HAS_SKILL]->(s)

        SET r.level = row.level
        """

        with neo4j_connection.driver.session() as session:

            session.run(
                query,
                records=employee_skills
            ).consume()

    # =========================================================
    # TASK REQUIRES SKILL
    # =========================================================

    def connect_task_skill(
        self,
        task_id,
        skill_id,
        required_level
    ):

        query = """
        MERGE (t:Task {
            task_id: $task_id
        })

        MATCH (s:Skill {
            skill_id: $skill_id
        })

        MERGE (t)-[r:REQUIRES]->(s)

        SET r.required_level = $required_level

        RETURN t, s, r
        """

        with neo4j_connection.driver.session() as session:

            result = session.run(
                query,
                task_id=str(task_id),
                skill_id=str(skill_id),
                required_level=float(required_level)
            )

            return result.single()

    # =========================================================
    # BATCH TASK -> SKILL
    # =========================================================

    def create_task_skills_batch(
        self,
        task_skills
    ):

        query = """
        UNWIND $records AS row

        MERGE (t:Task {
            task_id: row.task_id
        })

        MATCH (s:Skill {
            skill_id: row.skill_id
        })

        MERGE (t)-[r:REQUIRES]->(s)

        SET r.required_level = row.required_level
        """

        with neo4j_connection.driver.session() as session:

            session.run(
                query,
                records=task_skills
            ).consume()

    # =========================================================
    # FIND EMPLOYEES FOR TASK
    # =========================================================

    def find_employees_for_task(
        self,
        task_id
    ):

        query = """
        MATCH (t:Task {
            task_id: $task_id
        })

        MATCH (t)-[req:REQUIRES]->(s:Skill)

        MATCH (e:Employee)-[has:HAS_SKILL]->(s)

        RETURN
            e.employee_id AS employee_id,
            e.name AS name,

            collect({
                skill_id: s.skill_id,
                employee_level: has.level,
                required_level: req.required_level
            }) AS matched_skills

        ORDER BY size(matched_skills) DESC
        """

        with neo4j_connection.driver.session() as session:

            result = session.run(
                query,
                task_id=str(task_id)
            )

            return [
                record.data()
                for record in result
            ]