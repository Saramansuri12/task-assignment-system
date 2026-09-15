import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  getEmployee,
  getEmployeeAssignments,
  getEmployeeSkills,
  getEmployeeWorkload,
  getProjects,
  getSkills,
  getTasks,
} from "../services/api";
import {
  ArrowLeft,
  Briefcase,
  Clock,
  CheckCircle2,
  TrendingUp,
  Users,
} from "lucide-react";

export default function EmployeeDetails() {
  const navigate = useNavigate();
  const { id } = useParams();

  const [employee, setEmployee] = useState(null);
  const [skills, setSkills] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [workload, setWorkload] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(() => {
    if (!id) return Promise.resolve();

    setLoading(true);
    setError("");

    return Promise.all([
      getEmployee(id),
      getEmployeeSkills(id),
      getEmployeeAssignments(id),
      getSkills(),
      getTasks(),
      getProjects(),
      getEmployeeWorkload(id).catch(() => null),
    ])
      .then(
        ([
          employeeResult,
          employeeSkills,
          assignments,
          allSkills,
          allTasks,
          allProjects,
          workloadResult,
        ]) => {
          const skillNameById = new Map(
            allSkills.map((skill) => [skill.skill_id, skill.skill_name])
          );

          setEmployee(employeeResult);
          setWorkload(workloadResult);

          // Skills were never fetched before, so this card always
          // showed the same five hardcoded values.
          setSkills(
            employeeSkills.map((row) => ({
              id: row.skill_id,
              name: skillNameById.get(row.skill_id) || "Unknown skill",
              level: row.skill_level,
            }))
          );

          const taskById = new Map(
            allTasks.map((task) => [task.task_id, task])
          );

          const employeeTasks = assignments
            .map((assignment) => ({
              assignment,
              task: taskById.get(assignment.task_id),
            }))
            .filter((entry) => entry.task);

          setTasks(
            employeeTasks.map(({ assignment, task }) => ({
              id: assignment.assignment_id,
              taskId: task.task_id,
              title: task.task_title || task.task_id,
              project: task.project_id,
              status: assignment.status || "ACTIVE",
            }))
          );

          const projectById = new Map(
            allProjects.map((project) => [project.project_id, project])
          );

          const projectIds = [
            ...new Set(employeeTasks.map(({ task }) => task.project_id)),
          ];

          setProjects(
            projectIds.map((projectId) => {
              const project = projectById.get(projectId);

              const related = employeeTasks.filter(
                ({ task }) => task.project_id === projectId
              );

              const completed = related.filter(
                ({ assignment }) =>
                  (assignment.status || "").toUpperCase() === "COMPLETED"
              ).length;

              return {
                id: projectId,
                name: project?.project_domain || projectId,
                progress: related.length
                  ? Math.round((completed / related.length) * 100)
                  : 0,
                status: project?.priority || "Active",
              };
            })
          );
        }
      )
      .catch((exception) =>
        setError(exception.message || "Employee details could not be loaded.")
      )
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  if (loading) {
    return (
      <div className="employee-details-page">
        <p>Loading employee details...</p>
      </div>
    );
  }

  if (error || !employee) {
    return (
      <div className="employee-details-page">
        <button className="back-link" onClick={() => navigate("/team")}>
          <ArrowLeft size={16} />
          Back to Team
        </button>

        <div className="form-error">
          {error || "Employee not found."}{" "}
          <button type="button" className="text-button" onClick={load}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  const name = employee.name || `Employee ${employee.employee_id}`;
  const initials = name.slice(0, 2).toUpperCase();
  const availability =
    (employee.availability_pct ?? 0) >= 50 ? "Available" : "Busy";

  const completedTasks = tasks.filter(
    (task) => task.status.toUpperCase() === "COMPLETED"
  ).length;

  return (
    <div className="employee-details-page">

      <button className="back-link" onClick={() => navigate("/team")}>
        <ArrowLeft size={16} />
        Back to Team
      </button>

      {/* Profile Header */}

      <div className="employee-profile-header">
        <div className="employee-profile-main">
          <div className="employee-large-avatar">{initials}</div>

          <div>
            <p className="eyebrow">TEAM MEMBER · {employee.employee_id}</p>
            <h1>{name}</h1>
            <p className="employee-role">
              {employee.role || "Team member"}
              {employee.seniority ? ` · ${employee.seniority}` : ""}
            </p>
            <p className="employee-id">Employee ID: {employee.employee_id}</p>
          </div>
        </div>

        <span className="employee-availability-large">{availability}</span>
      </div>

      {/* Stats */}

      <div className="employee-details-stats">

        <div className="employee-detail-stat">
          <Briefcase size={18} />
          <div>
            <span>Active Projects</span>
            <strong>{projects.length}</strong>
          </div>
        </div>

        <div className="employee-detail-stat">
          <Clock size={18} />
          <div>
            <span>Current Workload</span>
            <strong>{employee.current_workload_pct ?? 0}%</strong>
          </div>
        </div>

        <div className="employee-detail-stat">
          <TrendingUp size={18} />
          <div>
            <span>Performance Score</span>
            <strong>{employee.performance_score ?? "-"}</strong>
          </div>
        </div>

        <div className="employee-detail-stat">
          <CheckCircle2 size={18} />
          <div>
            <span>Completed Tasks</span>
            <strong>{completedTasks}</strong>
          </div>
        </div>

      </div>

      <div className="employee-details-layout">

        <div className="employee-details-main">

          {/* Skills */}

          <section className="employee-details-card">
            <div className="details-card-header">
              <div>
                <h2>Skills &amp; Expertise</h2>
                <p>{skills.length} recorded skills</p>
              </div>
            </div>

            <div className="employee-skills-large">
              {skills.length === 0 ? (
                <p>No skills recorded for this employee.</p>
              ) : (
                skills.map((skill) => (
                  <span key={skill.id}>
                    {skill.name}
                    {skill.level != null ? ` (${skill.level})` : ""}
                  </span>
                ))
              )}
            </div>
          </section>

          {/* Projects */}

          <section className="employee-details-card">
            <div className="details-card-header">
              <div>
                <h2>Projects</h2>
                <p>Derived from current assignments</p>
              </div>
            </div>

            <div className="employee-project-list">
              {projects.length === 0 && <p>Not assigned to any project.</p>}

              {projects.map((project) => (
                <div
                  className="employee-project-row clickable-row"
                  key={project.id}
                  onClick={() => navigate(`/projects/${project.id}`)}
                >
                  <div className="employee-project-info">
                    <h3>{project.name}</h3>
                    <span>{project.status}</span>
                  </div>

                  <div className="employee-project-progress">
                    <strong>{project.progress}%</strong>

                    <div className="employee-progress-track">
                      <div
                        className="employee-progress-fill"
                        style={{ width: `${project.progress}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Tasks */}

          <section className="employee-details-card">
            <div className="details-card-header">
              <div>
                <h2>Assigned Tasks</h2>
                <p>{tasks.length} assignments</p>
              </div>
            </div>

            <div className="employee-task-list">
              {tasks.length === 0 && <p>No tasks assigned.</p>}

              {tasks.map((task) => (
                <div
                  className="employee-task-row clickable-row"
                  key={task.id}
                  onClick={() => navigate(`/tasks/${task.taskId}`)}
                >
                  <div className="employee-task-icon">
                    {task.status.toUpperCase() === "COMPLETED" ? (
                      <CheckCircle2 size={17} />
                    ) : (
                      <Clock size={17} />
                    )}
                  </div>

                  <div className="employee-task-info">
                    <h3>{task.title}</h3>
                    <p>{task.project}</p>
                  </div>

                  <span
                    className={`employee-task-status ${task.status
                      .toLowerCase()
                      .replaceAll("_", "-")}`}
                  >
                    {task.status}
                  </span>
                </div>
              ))}
            </div>
          </section>

        </div>

        <aside className="employee-details-sidebar">

          <div className="employee-details-card employee-workload-card">
            <h2>Current Workload</h2>

            <div className="employee-workload-circle">
              <strong>{employee.current_workload_pct ?? 0}%</strong>
              <span>Capacity Used</span>
            </div>

            {workload && (
              <p>
                {workload.remaining_capacity_pct}% capacity remaining across{" "}
                {workload.assigned_hours} assigned hours.
              </p>
            )}
          </div>

          <div className="employee-details-card employee-team-card">
            <Users size={18} />
            <h3>Experience</h3>
            <p>
              {employee.years_experience ?? 0} years of experience
              {employee.critical_project_experience
                ? ", with prior critical-project exposure."
                : "."}
            </p>
          </div>

        </aside>

      </div>

    </div>
  );
}
