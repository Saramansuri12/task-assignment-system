import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getProject, getSkills, getTasks, getTaskSkills } from "../services/api";
import {
  ArrowLeft,
  Check,
  Sparkles,
  ChevronRight,
  Plus,
  AlertCircle,
} from "lucide-react";

/**
 * Shows the real skill requirements recorded against a project's tasks.
 * The previous version displayed a hardcoded list of Python/FastAPI/
 * PostgreSQL regardless of the project.
 */
export default function RequirementsReview() {
  const navigate = useNavigate();
  const { id } = useParams();

  const [project, setProject] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [skillSummary, setSkillSummary] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(() => {
    if (!id) return Promise.resolve();

    setLoading(true);
    setError("");

    return Promise.all([getProject(id), getTasks(), getSkills()])
      .then(async ([projectResult, allTasks, allSkills]) => {
        const skillNameById = new Map(
          allSkills.map((skill) => [skill.skill_id, skill.skill_name])
        );

        const projectTasks = allTasks.filter(
          (task) => task.project_id === id
        );

        setProject(projectResult);
        setTasks(projectTasks);

        const aggregated = new Map();

        for (const task of projectTasks) {
          let rows = [];

          try {
            rows = await getTaskSkills(task.task_id);
          } catch {
            rows = [];
          }

          rows.forEach((row) => {
            const key = row.skill_id;

            const existing = aggregated.get(key) || {
              id: key,
              name: skillNameById.get(key) || "Unknown skill",
              maxLevel: 0,
              critical: false,
              taskCount: 0,
            };

            existing.maxLevel = Math.max(
              existing.maxLevel,
              row.required_level || 0
            );
            existing.critical = existing.critical || Boolean(row.is_critical);
            existing.taskCount += 1;

            aggregated.set(key, existing);
          });
        }

        setSkillSummary([...aggregated.values()]);
      })
      .catch((exception) =>
        setError(exception.message || "Requirements could not be loaded.")
      )
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  const roles = [
    ...new Set(
      tasks.map((task) => task.role_required).filter(Boolean)
    ),
  ];

  return (
    <div className="requirements-page">

      <button
        className="back-link"
        onClick={() => navigate(`/projects/${id}`)}
      >
        <ArrowLeft size={16} />
        Back to Project
      </button>

      <div className="requirements-heading">
        <div>
          <h1>Project Requirements</h1>
          <p>
            Skills and roles recorded against this project's tasks. These
            are exactly what the model matches candidates against.
          </p>
        </div>

        <div className="ai-badge">
          <Sparkles size={14} />
          {skillSummary.length} skills across {tasks.length} tasks
        </div>
      </div>

      {loading && <p>Loading requirements...</p>}
      {error && <p className="form-error">{error}</p>}

      <div className="project-steps requirements-steps">
        <div className="step completed">
          <div className="step-number"><Check size={14} /></div>
          <div>
            <strong>Project Created</strong>
            <span>Completed</span>
          </div>
        </div>

        <div className="step-line completed-line" />

        <div className="step active">
          <div className="step-number">2</div>
          <div>
            <strong>Requirements</strong>
            <span>Review skills</span>
          </div>
        </div>

        <div className="step-line" />

        <div className="step">
          <div className="step-number">3</div>
          <div>
            <strong>Team Match</strong>
            <span>Model recommendation</span>
          </div>
        </div>
      </div>

      <div className="requirements-layout">

        <div className="requirements-main">

          <section className="requirements-card">
            <div className="requirements-card-header">
              <div>
                <h2>Required Skills</h2>
                <p>Aggregated across every task in this project</p>
              </div>

              <button
                className="add-button"
                onClick={() => navigate("/tasks/new")}
              >
                <Plus size={14} />
                Add Task
              </button>
            </div>

            <div className="skills-list">
              {!loading && skillSummary.length === 0 && (
                <p>
                  No skill requirements recorded yet. Create a task and add
                  required skills so the model has something to match on.
                </p>
              )}

              {skillSummary.map((skill) => (
                <div className="skill-review-row" key={skill.id}>
                  <div className="skill-review-icon">
                    {skill.critical ? (
                      <AlertCircle size={15} />
                    ) : (
                      <Sparkles size={15} />
                    )}
                  </div>

                  <div className="skill-review-info">
                    <h3>{skill.name}</h3>
                    <span>
                      Required by {skill.taskCount} task
                      {skill.taskCount === 1 ? "" : "s"}
                    </span>
                  </div>

                  <span className="skill-level">
                    Level {skill.maxLevel}
                    {skill.critical ? " · Critical" : ""}
                  </span>
                </div>
              ))}
            </div>
          </section>

          <section className="requirements-card">
            <div className="requirements-card-header">
              <div>
                <h2>Roles Required</h2>
                <p>Taken from the role_required field on each task</p>
              </div>
            </div>

            <div className="technology-tags">
              {roles.length === 0 && <p>No roles specified.</p>}

              {roles.map((role) => (
                <span className="technology-tag" key={role}>
                  {role}
                </span>
              ))}
            </div>
          </section>

          <section className="requirements-card">
            <div className="requirements-card-header">
              <div>
                <h2>Tasks</h2>
                <p>Open a task to get recommendations</p>
              </div>
            </div>

            <div className="skills-list">
              {tasks.length === 0 && <p>No tasks in this project yet.</p>}

              {tasks.map((task) => (
                <div
                  className="skill-review-row clickable-row"
                  key={task.task_id}
                  onClick={() => navigate(`/tasks/${task.task_id}`)}
                >
                  <div className="skill-review-info">
                    <h3>{task.task_title || task.task_id}</h3>
                    <span>
                      {task.role_required || "No role"} ·{" "}
                      {task.priority || "No priority"}
                    </span>
                  </div>

                  <ChevronRight size={16} />
                </div>
              ))}
            </div>
          </section>

        </div>

        <aside className="project-summary-card">
          <div className="summary-card-heading">
            <h2>Project Summary</h2>
          </div>

          <div className="summary-project-name">
            {project?.project_domain || id}
          </div>

          <p className="summary-description">
            {project?.project_type || "No type recorded."}
          </p>

          <div className="summary-details">
            <div className="summary-detail">
              <span>Complexity</span>
              <strong>{project?.project_complexity || "Not set"}</strong>
            </div>

            <div className="summary-detail">
              <span>Criticality</span>
              <strong>{project?.project_criticality || "Not set"}</strong>
            </div>

            <div className="summary-detail">
              <span>Priority</span>
              <strong>{project?.priority || "Not set"}</strong>
            </div>

            <div className="summary-detail">
              <span>Deadline</span>
              <strong>{project?.end_date || "Not set"}</strong>
            </div>
          </div>
        </aside>

      </div>

    </div>
  );
}
