import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  getAssignments,
  getEmployees,
  getProject,
  getTasks,
} from "../services/api";
import {
  ArrowLeft,
  Users,
  Calendar,
  CheckCircle2,
  Clock,
  Plus,
  ListTodo,
  Sparkles,
} from "lucide-react";

export default function ProjectDetails() {
  const navigate = useNavigate();
  const { id } = useParams();

  const [project, setProject] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [team, setTeam] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(() => {
    if (!id) return Promise.resolve();

    setLoading(true);
    setError("");

    return Promise.all([
      getProject(id),
      getTasks(),
      getAssignments(),
      getEmployees(),
    ])
      .then(([projectResult, allTasks, assignments, employees]) => {
        const projectTasks = allTasks.filter(
          (task) => task.project_id === id
        );

        const projectTaskIds = new Set(
          projectTasks.map((task) => task.task_id)
        );

        const projectAssignments = assignments.filter((assignment) =>
          projectTaskIds.has(assignment.task_id)
        );

        const employeeById = new Map(
          employees.map((employee) => [
            String(employee.employee_id),
            employee,
          ])
        );

        setProject(projectResult);

        setTasks(
          projectTasks.map((task) => {
            const related = projectAssignments.filter(
              (assignment) => assignment.task_id === task.task_id
            );

            return {
              ...task,
              assigneeNames: related.map(
                (assignment) =>
                  employeeById.get(String(assignment.employee_id))?.name ||
                  assignment.employee_id
              ),
              status: related.length
                ? related[0].status || "ACTIVE"
                : "Unassigned",
            };
          })
        );

        // Team is built from real assignments, not a hardcoded roster.
        const seen = new Map();

        projectAssignments.forEach((assignment) => {
          const key = String(assignment.employee_id);
          const employee = employeeById.get(key);
          const name = employee?.name || assignment.employee_id;

          const entry = seen.get(key) || {
            id: key,
            name,
            initials: String(name).slice(0, 2).toUpperCase(),
            role: employee?.role || "Team member",
            taskCount: 0,
            bestScore: null,
          };

          entry.taskCount += 1;

          if (assignment.success_probability != null) {
            const pct = Math.round(assignment.success_probability * 100);
            entry.bestScore = Math.max(entry.bestScore ?? 0, pct);
          }

          seen.set(key, entry);
        });

        setTeam([...seen.values()]);
      })
      .catch((exception) =>
        setError(exception.message || "Project details could not be loaded.")
      )
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  if (loading) {
    return (
      <div className="project-details-page">
        <p>Loading project...</p>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="project-details-page">
        <button className="back-link" onClick={() => navigate("/projects")}>
          <ArrowLeft size={16} />
          Back to Projects
        </button>

        <div className="form-error">
          {error || "Project not found."}{" "}
          <button type="button" className="text-button" onClick={load}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  const completed = tasks.filter(
    (task) => String(task.status).toUpperCase() === "COMPLETED"
  ).length;

  const progress = tasks.length
    ? Math.round((completed / tasks.length) * 100)
    : 0;

  return (
    <div className="project-details-page">

      <button className="back-link" onClick={() => navigate("/projects")}>
        <ArrowLeft size={16} />
        Back to Projects
      </button>

      <div className="dashboard-header">
        <div>
          <p className="eyebrow">PROJECT · {project.project_id}</p>
          <h1>{project.project_name || project.project_domain || project.project_id}</h1>
          <p className="dashboard-description">
            {project.project_type || "No project type recorded."}
          </p>
        </div>

        <button
          className="primary-button"
          onClick={() => navigate("/tasks/new")}
        >
          <Plus size={17} />
          Add Task
        </button>
      </div>

      <div className="task-stats-grid">

        <div className="task-stat-card">
          <ListTodo size={19} />
          <div>
            <span>Tasks</span>
            <strong>{tasks.length}</strong>
          </div>
        </div>

        <div className="task-stat-card">
          <Users size={19} />
          <div>
            <span>Team Members</span>
            <strong>{team.length}</strong>
          </div>
        </div>

        <div className="task-stat-card">
          <CheckCircle2 size={19} />
          <div>
            <span>Progress</span>
            <strong>{progress}%</strong>
          </div>
        </div>

        <div className="task-stat-card">
          <Calendar size={19} />
          <div>
            <span>Deadline</span>
            <strong>{project.end_date || "Not set"}</strong>
          </div>
        </div>

      </div>

      <div className="employee-details-layout">

        <div className="employee-details-main">

          <section className="employee-details-card">
            <div className="details-card-header">
              <div>
                <h2>Tasks</h2>
                <p>Open a task to request recommendations</p>
              </div>

              <button
                className="text-button"
                onClick={() => navigate(`/projects/${id}/requirements`)}
              >
                <Sparkles size={15} />
                View requirements
              </button>
            </div>

            <div className="employee-task-list">
              {tasks.length === 0 && (
                <p>No tasks yet. Add one to start assigning work.</p>
              )}

              {tasks.map((task) => (
                <div
                  className="employee-task-row clickable-row"
                  key={task.task_id}
                  onClick={() => navigate(`/tasks/${task.task_id}`)}
                >
                  <div className="employee-task-icon">
                    {String(task.status).toUpperCase() === "COMPLETED" ? (
                      <CheckCircle2 size={17} />
                    ) : (
                      <Clock size={17} />
                    )}
                  </div>

                  <div className="employee-task-info">
                    <h3>{task.task_title || task.task_id}</h3>
                    <p>
                      {task.assigneeNames.length
                        ? task.assigneeNames.join(", ")
                        : "Unassigned"}
                    </p>
                  </div>

                  <span
                    className={`employee-task-status ${String(task.status)
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

          <div className="employee-details-card">
            <h2>Assigned Team</h2>

            {team.length === 0 && <p>Nobody assigned yet.</p>}

            {team.map((member) => (
              <div
                className="alternative-member clickable-row"
                key={member.id}
                onClick={() => navigate(`/team/${member.id}`)}
              >
                <div className="alternative-avatar">{member.initials}</div>

                <div className="alternative-info">
                  <strong>{member.name}</strong>
                  <span>
                    {member.role} · {member.taskCount} task
                    {member.taskCount === 1 ? "" : "s"}
                  </span>
                </div>

                {member.bestScore != null && (
                  <div className="alternative-match">{member.bestScore}%</div>
                )}
              </div>
            ))}
          </div>

          <div className="employee-details-card">
            <h2>Details</h2>

            <div className="summary-details">
              <div className="summary-detail">
                <span>Complexity</span>
                <strong>{project.project_complexity || "Not set"}</strong>
              </div>

              <div className="summary-detail">
                <span>Criticality</span>
                <strong>{project.project_criticality || "Not set"}</strong>
              </div>

              <div className="summary-detail">
                <span>Priority</span>
                <strong>{project.priority || "Not set"}</strong>
              </div>

              <div className="summary-detail">
                <span>Start</span>
                <strong>{project.start_date || "Not set"}</strong>
              </div>
            </div>
          </div>

        </aside>

      </div>

    </div>
  );
}
