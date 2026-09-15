import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  getAssignments,
  getEmployees,
  getEmployeeSkills,
  getSkills,
} from "../services/api";
import {
  Search,
  Users,
  Briefcase,
  Clock,
  CheckCircle2,
} from "lucide-react";

export default function TeamManagement() {
  const [search, setSearch] = useState("");
  const navigate = useNavigate();

  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(() => {
    setLoading(true);
    setError("");

    return Promise.all([getEmployees(), getSkills(), getAssignments()])
      .then(async ([employeeRecords, skillRecords, assignments]) => {
        const skillNameById = new Map(
          skillRecords.map((skill) => [skill.skill_id, skill.skill_name])
        );

        const assignmentCount = new Map();

        assignments.forEach((assignment) => {
          const key = String(assignment.employee_id);
          assignmentCount.set(key, (assignmentCount.get(key) || 0) + 1);
        });

        // Skills come from /employee-skills/employee/{id}. Fetching one
        // request per employee would hammer the API on a large roster,
        // so only the first 60 rows are enriched.
        const enriched = await Promise.all(
          employeeRecords.map(async (employee, index) => {
            let skills = [];

            if (index < 60) {
              try {
                const rows = await getEmployeeSkills(employee.employee_id);
                skills = rows
                  .map(
                    (row) => skillNameById.get(row.skill_id) || "Unknown skill"
                  )
                  .slice(0, 6);
              } catch {
                skills = [];
              }
            }

            const name =
              employee.name || `Employee ${employee.employee_id}`;

            return {
              id: employee.employee_id,
              name,
              initials: name.slice(0, 2).toUpperCase(),
              role: employee.role || "Team member",
              availability:
                (employee.availability_pct ?? 0) >= 50 ? "Available" : "Busy",
              availabilityPct: employee.availability_pct ?? 0,
              workload: employee.current_workload_pct ?? 0,
              projects: assignmentCount.get(String(employee.employee_id)) || 0,
              skills,
            };
          })
        );

        setEmployees(enriched);
      })
      .catch((exception) =>
        setError(exception.message || "Employee data could not be loaded.")
      )
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const filteredEmployees = employees.filter((employee) => {
    const searchText = search.toLowerCase();

    return (
      employee.name.toLowerCase().includes(searchText) ||
      employee.role.toLowerCase().includes(searchText) ||
      employee.id.toLowerCase().includes(searchText) ||
      employee.skills.some((skill) =>
        String(skill).toLowerCase().includes(searchText)
      )
    );
  });

  const availableEmployees = employees.filter(
    (employee) => employee.availability === "Available"
  ).length;

  const averageWorkload = employees.length
    ? Math.round(
        employees.reduce((total, employee) => total + employee.workload, 0) /
          employees.length
      )
    : 0;

  const totalAssignments = employees.reduce(
    (total, employee) => total + employee.projects,
    0
  );

  return (
    <div className="team-management-page">

      {/* ================= HEADER ================= */}

      <div className="team-management-header">
        <div>
          <p className="eyebrow">TEAM MANAGEMENT</p>
          <h1>Team Members</h1>
          <p>
            Employee skills, availability, workload and current
            assignments, straight from the database.
          </p>
        </div>
      </div>

      {loading && <p>Loading team members...</p>}

      {error && (
        <div className="form-error">
          {error}{" "}
          <button type="button" className="text-button" onClick={load}>
            Retry
          </button>
        </div>
      )}

      {/* ================= STATS ================= */}

      <div className="team-management-stats">

        <div className="team-stat-card">
          <Users size={19} />
          <div>
            <span>Total Employees</span>
            <strong>{employees.length}</strong>
          </div>
        </div>

        <div className="team-stat-card">
          <CheckCircle2 size={19} />
          <div>
            <span>Available</span>
            <strong>{availableEmployees}</strong>
          </div>
        </div>

        <div className="team-stat-card">
          <Clock size={19} />
          <div>
            <span>Average Workload</span>
            <strong>{averageWorkload}%</strong>
          </div>
        </div>

        <div className="team-stat-card">
          <Briefcase size={19} />
          <div>
            <span>Active Assignments</span>
            <strong>{totalAssignments}</strong>
          </div>
        </div>

      </div>

      {/* ================= SEARCH ================= */}

      <div className="team-management-controls">
        <div className="employee-search">
          <Search size={17} />

          <input
            type="text"
            placeholder="Search employees, roles, or skills..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
      </div>

      {/* ================= EMPLOYEE TABLE ================= */}

      <div className="employee-table-card">

        <div className="employee-table-header">
          <span>Employee</span>
          <span>Skills</span>
          <span>Availability</span>
          <span>Workload</span>
          <span>Assignments</span>
        </div>

        <div className="employee-table-body">

          {filteredEmployees.length > 0 ? (
            filteredEmployees.map((employee) => (
              <div
                className="employee-row clickable-row"
                key={employee.id}
                onClick={() => navigate(`/team/${employee.id}`)}
              >

                <div className="employee-profile">
                  <div className="employee-avatar">{employee.initials}</div>

                  <div>
                    <h3>{employee.name}</h3>
                    <p>{employee.role}</p>
                    <p>Employee ID: {employee.id}</p>
                  </div>
                </div>

                <div className="employee-skills">
                  {employee.skills.length === 0 ? (
                    <span>No skills recorded</span>
                  ) : (
                    employee.skills.map((skill) => (
                      <span key={skill}>{skill}</span>
                    ))
                  )}
                </div>

                <div>
                  <span
                    className={`availability-badge ${employee.availability
                      .toLowerCase()
                      .replaceAll(" ", "-")}`}
                  >
                    {employee.availability}
                  </span>
                </div>

                <div className="workload-column">
                  <strong>{employee.workload}%</strong>

                  <div className="workload-bar">
                    <div
                      className="workload-fill"
                      style={{ width: `${employee.workload}%` }}
                    />
                  </div>
                </div>

                <div className="project-count">{employee.projects}</div>

              </div>
            ))
          ) : (
            !loading && (
              <div className="no-employees-found">
                <Users size={28} />
                <h3>No employees found</h3>
                <p>
                  {employees.length === 0
                    ? "There are no employees in the database yet."
                    : "Try a different name, role, or skill."}
                </p>
              </div>
            )
          )}

        </div>

      </div>

    </div>
  );
}
