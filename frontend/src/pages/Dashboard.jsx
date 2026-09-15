import {
  FolderKanban,
  Users,
  CheckCircle2,
  Clock3,
  Plus,
  ArrowRight,
  ListTodo,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useCallback, useEffect, useState } from "react";
import {
  getAssignments,
  getDashboardSummary,
  getProjects,
  getTasks,
} from "../services/api";

export default function Dashboard() {
  const navigate = useNavigate();

  const [summary, setSummary] = useState(null);
  const [projects, setProjects] = useState([]);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(() => {
    setLoading(true);
    setError("");

    // getDashboardSummary was called here but never imported, which
    // threw a ReferenceError on mount and blanked the whole app.
    return Promise.all([
      getDashboardSummary(),
      getProjects(),
      getTasks(),
      getAssignments(),
    ])
      .then(([dashboardSummary, projectRecords, taskRecords, assignmentRecords]) => {
        setSummary(dashboardSummary);

        const statusWeight = (status) => {
          const value = (status || "").toUpperCase();
          if (value === "COMPLETED") return 100;
          if (value === "IN_PROGRESS" || value === "ACTIVE") return 50;
          return 0;
        };

        setProjects(
          projectRecords.map((project) => {
            const projectTasks = taskRecords.filter(
              (task) => task.project_id === project.project_id
            );

            const projectTaskIds = new Set(
              projectTasks.map((task) => task.task_id)
            );

            const projectAssignments = assignmentRecords.filter(
              (assignment) => projectTaskIds.has(assignment.task_id)
            );

            const progress = projectAssignments.length
              ? Math.round(
                  projectAssignments.reduce(
                    (total, assignment) =>
                      total + statusWeight(assignment.status),
                    0
                  ) / projectAssignments.length
                )
              : 0;

            return {
              id: project.project_id,
              name: project.project_name || project.project_domain || project.project_id,
              type: project.project_type || "Project",
              taskCount: projectTasks.length,
              team: new Set(
                projectAssignments.map((assignment) => assignment.employee_id)
              ).size,
              progress,
              status:
                progress === 100
                  ? "Completed"
                  : projectAssignments.length
                  ? "In Progress"
                  : "Not started",
              deadline: project.end_date || "Not set",
            };
          })
        );

        // Derived from real assignment records rather than a
        // hardcoded activity feed.
        const taskById = new Map(
          taskRecords.map((task) => [task.task_id, task])
        );

        setActivities(
          assignmentRecords.slice(0, 6).map((assignment) => ({
            id: assignment.assignment_id,
            title: `${assignment.employee_id} assigned to ${
              taskById.get(assignment.task_id)?.task_title ||
              assignment.task_id
            }`,
            status: assignment.status || "ACTIVE",
            score:
              assignment.success_probability != null
                ? `${Math.round(assignment.success_probability * 100)}% predicted success`
                : null,
          }))
        );
      })
      .catch((exception) =>
        setError(exception.message || "Dashboard data could not be loaded.")
      )
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="dashboard">

      {/* Header */}
      <div className="dashboard-header">
        <div>
          <p className="eyebrow">PROJECT MANAGER</p>
          <h1>Workforce overview</h1>

          <p className="dashboard-description">
            Live figures from your database. Create a project, add tasks,
            then let the model recommend who should take them.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={() => navigate("/projects/new")}
        >
          <Plus size={18} />
          Create New Project
        </button>
      </div>

      {loading && <p>Loading dashboard...</p>}

      {error && (
        <div className="form-error">
          {error}{" "}
          <button type="button" className="text-button" onClick={load}>
            Retry
          </button>
        </div>
      )}

      {/* Summary Cards */}
      {summary && (
        <div className="summary-grid">

          <div className="summary-card">
            <div className="summary-card-top">
              <div className="summary-icon blue">
                <FolderKanban size={20} />
              </div>
            </div>

            <div className="summary-number">{summary.projects.total}</div>
            <div className="summary-label">Total Projects</div>
          </div>

          <div className="summary-card">
            <div className="summary-card-top">
              <div className="summary-icon purple">
                <Users size={20} />
              </div>
            </div>

            <div className="summary-number">{summary.employees.total}</div>
            <div className="summary-label">Team Members</div>
          </div>

          <div className="summary-card">
            <div className="summary-card-top">
              <div className="summary-icon green">
                <CheckCircle2 size={20} />
              </div>
            </div>

            <div className="summary-number">{summary.success_rate}%</div>
            <div className="summary-label">Predicted Success Rate</div>
          </div>

          <div className="summary-card">
            <div className="summary-card-top">
              <div className="summary-icon orange">
                <Clock3 size={20} />
              </div>
            </div>

            <div className="summary-number">{summary.assignments.active}</div>
            <div className="summary-label">Active Assignments</div>
          </div>

        </div>
      )}

      {summary && (
        <div className="summary-grid">

          <div className="summary-card">
            <div className="summary-card-top">
              <div className="summary-icon blue">
                <ListTodo size={20} />
              </div>
            </div>
            <div className="summary-number">{summary.tasks.total}</div>
            <div className="summary-label">Total Tasks</div>
          </div>

          <div className="summary-card">
            <div className="summary-card-top">
              <div className="summary-icon purple">
                <ClipboardIcon />
              </div>
            </div>
            <div className="summary-number">{summary.assignments.total}</div>
            <div className="summary-label">Total Assignments</div>
          </div>

          <div className="summary-card">
            <div className="summary-card-top">
              <div className="summary-icon green">
                <CheckCircle2 size={20} />
              </div>
            </div>
            <div className="summary-number">
              {summary.assignments.completed}
            </div>
            <div className="summary-label">Completed</div>
          </div>

          <div className="summary-card">
            <div className="summary-card-top">
              <div className="summary-icon orange">
                <CheckCircle2 size={20} />
              </div>
            </div>
            <div className="summary-number">
              {summary.assignments.successful}
            </div>
            <div className="summary-label">Predicted Successful</div>
          </div>

        </div>
      )}

      {/* Main Grid */}
      <div className="dashboard-grid">

        {/* Projects */}
        <section className="dashboard-section projects-section">

          <div className="section-header">
            <div>
              <h2>Projects</h2>
              <p>Progress based on assignment status</p>
            </div>

            <button
              className="text-button"
              onClick={() => navigate("/projects")}
            >
              View all
              <ArrowRight size={16} />
            </button>
          </div>

          <div className="project-list">

            {!loading && projects.length === 0 && (
              <p>No projects yet. Create one to get started.</p>
            )}

            {projects.slice(0, 6).map((project) => (
              <div
                className="project-row clickable-row"
                key={project.id}
                onClick={() => navigate(`/projects/${project.id}`)}
              >

                <div className="project-main">
                  <div className="project-icon">
                    <FolderKanban size={19} />
                  </div>

                  <div>
                    <h3>{project.name}</h3>

                    <div className="project-meta">
                      <span>
                        <Users size={13} />
                        {project.team} assigned
                      </span>

                      <span>{project.taskCount} tasks</span>

                      <span>Deadline: {project.deadline}</span>
                    </div>
                  </div>
                </div>

                <div className="project-progress">
                  <div className="progress-info">
                    <span>Progress</span>
                    <strong>{project.progress}%</strong>
                  </div>

                  <div className="progress-track">
                    <div
                      className="progress-fill"
                      style={{ width: `${project.progress}%` }}
                    />
                  </div>
                </div>

                <div className="project-status">{project.status}</div>

              </div>
            ))}

          </div>
        </section>

        {/* Activity */}
        <section className="dashboard-section activity-section">

          <div className="section-header">
            <div>
              <h2>Recent Assignments</h2>
              <p>Latest allocation activity</p>
            </div>
          </div>

          <div className="activity-list">

            {!loading && activities.length === 0 && (
              <p>No assignments recorded yet.</p>
            )}

            {activities.map((activity) => (
              <div className="activity-item" key={activity.id}>

                <div className="activity-icon">
                  <CheckCircle2 size={17} />
                </div>

                <div className="activity-content">
                  <div className="activity-title">{activity.title}</div>
                  <div className="activity-time">
                    {activity.status}
                    {activity.score ? ` · ${activity.score}` : ""}
                  </div>
                </div>

              </div>
            ))}

          </div>

        </section>

      </div>

      {/* Quick Action */}
      <section className="smart-action">

        <div className="smart-action-icon">✨</div>

        <div className="smart-action-content">
          <h3>Let the model find the right people for a task</h3>

          <p>
            Open any task and request recommendations. The trained XGBoost
            model scores every eligible employee on skill match, critical
            skill coverage, experience, workload and availability.
          </p>
        </div>

        <button
          className="secondary-button"
          onClick={() => navigate("/tasks")}
        >
          Go to Tasks
          <ArrowRight size={17} />
        </button>

      </section>

    </div>
  );
}

function ClipboardIcon() {
  return <ListTodo size={20} />;
}
