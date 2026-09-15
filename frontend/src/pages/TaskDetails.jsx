import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  createAssignment,
  getAssignmentRecommendations,
  getEmployees,
  getSkills,
  getTask,
  getTaskAssignments,
  getTaskSkills,
  updateAssignmentStatus,
} from "../services/api";
import {
  ArrowLeft,
  Calendar,
  Flag,
  Sparkles,
  CheckCircle2,
  Users,
  Clock,
  AlertCircle,
} from "lucide-react";

export default function TaskDetails() {
  const navigate = useNavigate();
  const { id } = useParams();

  const [task, setTask] = useState(null);
  const [requiredSkills, setRequiredSkills] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [employeeById, setEmployeeById] = useState(new Map());

  const [recommendation, setRecommendation] = useState(null);
  const [recommendationError, setRecommendationError] = useState("");
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionMessage, setActionMessage] = useState("");
  const [actionError, setActionError] = useState("");
  const [busyEmployee, setBusyEmployee] = useState(null);

  /* ---------------- load core task data ---------------- */

  const loadTask = useCallback(() => {
    if (!id) return Promise.resolve();

    setLoading(true);
    setError("");

    return Promise.all([
      getTask(id),
      getTaskSkills(id),
      getTaskAssignments(id),
      getSkills(),
      getEmployees(),
    ])
      .then(([taskResult, taskSkills, taskAssignments, skills, employees]) => {
        const skillNameById = new Map(
          skills.map((skill) => [skill.skill_id, skill.skill_name])
        );

        setTask(taskResult);

        setRequiredSkills(
          taskSkills.map((row) => ({
            id: row.skill_id,
            name: skillNameById.get(row.skill_id) || "Unknown skill",
            level: row.required_level,
            critical: Boolean(row.is_critical),
          }))
        );

        setAssignments(taskAssignments);

        setEmployeeById(
          new Map(
            employees.map((employee) => [
              String(employee.employee_id),
              employee,
            ])
          )
        );
      })
      .catch((exception) =>
        setError(exception.message || "Task details could not be loaded.")
      )
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    loadTask();
  }, [loadTask]);

  /* ---------------- ML recommendations ---------------- */

  const loadRecommendations = useCallback(() => {
    if (!id) return;

    setLoadingRecommendations(true);
    setRecommendationError("");

    getAssignmentRecommendations(id, 10)
      .then(setRecommendation)
      .catch((exception) =>
        setRecommendationError(
          exception.message || "Recommendations could not be generated."
        )
      )
      .finally(() => setLoadingRecommendations(false));
  }, [id]);

  /* ---------------- assign ---------------- */

  const handleAssign = async (employeeId) => {
    setActionError("");
    setActionMessage("");
    setBusyEmployee(employeeId);

    try {
      await createAssignment(id, employeeId);
      setActionMessage(`${employeeId} assigned to this task.`);
      await loadTask();
      loadRecommendations();
    } catch (exception) {
      setActionError(exception.message || "Assignment failed.");
    } finally {
      setBusyEmployee(null);
    }
  };

  const handleStatusChange = async (assignmentId, status) => {
    setActionError("");
    setActionMessage("");

    try {
      await updateAssignmentStatus(assignmentId, status);
      setActionMessage(`Assignment ${assignmentId} set to ${status}.`);
      await loadTask();
    } catch (exception) {
      setActionError(exception.message || "Status update failed.");
    }
  };

  const assignedIds = new Set(
    assignments.map((assignment) => String(assignment.employee_id))
  );

  if (loading) {
    return (
      <div className="task-details-page">
        <p>Loading task...</p>
      </div>
    );
  }

  if (error || !task) {
    return (
      <div className="task-details-page">
        <button className="back-link" onClick={() => navigate("/tasks")}>
          <ArrowLeft size={16} />
          Back to Tasks
        </button>

        <div className="form-error">
          {error || "Task not found."}{" "}
          <button type="button" className="text-button" onClick={loadTask}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="task-details-page">

      <button className="back-link" onClick={() => navigate("/tasks")}>
        <ArrowLeft size={16} />
        Back to Tasks
      </button>

      {/* ================= HEADER ================= */}

      <div className="dashboard-header">
        <div>
          <p className="eyebrow">TASK · {task.task_id}</p>
          <h1>{task.task_title || task.task_id}</h1>
          <p className="dashboard-description">
            {task.task_description || "No description provided."}
          </p>
        </div>
      </div>

      {actionMessage && (
        <p className="form-success">{actionMessage}</p>
      )}

      {actionError && <p className="form-error">{actionError}</p>}

      {/* ================= META ================= */}

      <div className="task-stats-grid">

        <div className="task-stat-card">
          <Flag size={19} />
          <div>
            <span>Priority</span>
            <strong>{task.priority || "Not set"}</strong>
          </div>
        </div>

        <div className="task-stat-card">
          <Calendar size={19} />
          <div>
            <span>Due</span>
            <strong>{task.task_due_date || "No deadline"}</strong>
          </div>
        </div>

        <div className="task-stat-card">
          <Users size={19} />
          <div>
            <span>Team size required</span>
            <strong>{task.team_size_required ?? 1}</strong>
          </div>
        </div>

        <div className="task-stat-card">
          <Clock size={19} />
          <div>
            <span>Estimated hours</span>
            <strong>{task.estimated_hours ?? "Not set"}</strong>
          </div>
        </div>

      </div>

      {/* ================= REQUIRED SKILLS ================= */}

      <section className="employee-details-card">
        <div className="details-card-header">
          <div>
            <h2>Required Skills</h2>
            <p>Used by the model to score every candidate</p>
          </div>
        </div>

        <div className="employee-skills-large">
          {requiredSkills.length === 0 ? (
            <p>
              No skills recorded for this task. Recommendations will rely on
              role, experience and workload only.
            </p>
          ) : (
            requiredSkills.map((skill) => (
              <span key={skill.id}>
                {skill.name}
                {skill.critical ? " ★" : ""} (level {skill.level ?? "-"})
              </span>
            ))
          )}
        </div>
      </section>

      {/* ================= CURRENT ASSIGNMENTS ================= */}

      <section className="employee-details-card">
        <div className="details-card-header">
          <div>
            <h2>Current Assignments</h2>
            <p>{assignments.length} on this task</p>
          </div>
        </div>

        <div className="employee-task-list">
          {assignments.length === 0 && <p>Nobody is assigned yet.</p>}

          {assignments.map((assignment) => {
            const employee = employeeById.get(
              String(assignment.employee_id)
            );

            return (
              <div
                className="employee-task-row"
                key={assignment.assignment_id}
              >
                <div className="employee-task-icon">
                  <CheckCircle2 size={17} />
                </div>

                <div className="employee-task-info">
                  <h3>{employee?.name || assignment.employee_id}</h3>
                  <p>Employee ID: {assignment.employee_id}</p>
                  <p>
                    {assignment.assignment_id}
                    {assignment.success_probability != null
                      ? ` · ${Math.round(
                          assignment.success_probability * 100
                        )}% predicted success`
                      : ""}
                  </p>
                </div>

                <select
                  value={assignment.status || "ACTIVE"}
                  onChange={(event) =>
                    handleStatusChange(
                      assignment.assignment_id,
                      event.target.value
                    )
                  }
                >
                  {[
                    "PENDING",
                    "ACTIVE",
                    "IN_PROGRESS",
                    "COMPLETED",
                    "CANCELLED",
                    "REJECTED",
                  ].map((value) => (
                    <option key={value} value={value}>
                      {value}
                    </option>
                  ))}
                </select>
              </div>
            );
          })}
        </div>
      </section>

      {/* ================= RECOMMENDATIONS ================= */}

      <section className="employee-details-card">

        <div className="details-card-header">
          <div>
            <h2>Recommended Employees</h2>
            <p>
              {recommendation
                ? `${recommendation.eligible_candidates} of ${recommendation.total_candidates} candidates eligible · scored by ${
                    recommendation.scoring_method === "ml_model"
                      ? "the trained XGBoost model"
                      : "the rule-based fallback"
                  }`
                : "Run the model against every employee in the database"}
            </p>
          </div>

          <button
            className="primary-button"
            onClick={loadRecommendations}
            disabled={loadingRecommendations}
          >
            <Sparkles size={16} />
            {loadingRecommendations
              ? "Scoring..."
              : recommendation
              ? "Refresh"
              : "Get Recommendations"}
          </button>
        </div>

        {recommendationError && (
          <p className="form-error">{recommendationError}</p>
        )}

        {recommendation?.showing_near_misses && (
          <p className="form-error">
            <AlertCircle size={14} /> No employee met every eligibility rule.
            Showing the closest matches instead.
          </p>
        )}

        <div className="recommended-members">
          {recommendation?.recommendations?.length === 0 && (
            <p>No candidates available.</p>
          )}

          {recommendation?.recommendations?.map((member) => {
            const alreadyAssigned = assignedIds.has(
              String(member.employee_id)
            );

            return (
              <div className="team-member-card" key={member.employee_id}>

                <div className="member-card-top">
                  <div className="member-profile">
                    <div className="member-avatar">
                      {(member.name || member.employee_id)
                        .slice(0, 2)
                        .toUpperCase()}
                    </div>

                    <div>
                      <h3>{member.name || member.employee_id}</h3>
                      <p>{member.role || "Team member"}</p>
                      <p>Employee ID: {member.employee_id}</p>
                    </div>
                  </div>

                  <div className="member-match">
                    <span>
                      {recommendation.scoring_method === "ml_model"
                        ? "Predicted success"
                        : "Match score"}
                    </span>
                    <strong>{member.score}%</strong>
                  </div>
                </div>

                <div className="member-details">
                  <div>
                    <CheckCircle2 size={14} />
                    <span>{member.skill_match_pct}% skill match</span>
                  </div>

                  <div>
                    <Sparkles size={14} />
                    <span>
                      {member.critical_skill_match_pct}% critical skills
                    </span>
                  </div>

                  <div>
                    <Clock size={14} />
                    <span>{member.current_workload_pct ?? 0}% workload</span>
                  </div>
                </div>

                <div className="ai-reason">
                  <Sparkles size={14} />
                  <div>
                    <strong>Why this employee</strong>
                    <p>{member.reason}</p>
                  </div>
                </div>

                <button
                  className="primary-button"
                  disabled={
                    alreadyAssigned || busyEmployee === member.employee_id
                  }
                  onClick={() => handleAssign(member.employee_id)}
                >
                  {alreadyAssigned
                    ? "Already assigned"
                    : busyEmployee === member.employee_id
                    ? "Assigning..."
                    : "Assign to task"}
                </button>

              </div>
            );
          })}
        </div>

        {recommendation?.rejected_employees?.length > 0 && (
          <div className="details-card-header" style={{ marginTop: "1.5rem" }}>
            <div>
              <h2>Not eligible</h2>
              <ul>
                {recommendation.rejected_employees
                  .slice(0, 5)
                  .map((item) => (
                    <li key={item.employee_id}>
                      <strong>{item.name || item.employee_id}</strong>
                      {" — "}
                      {item.reasons.join("; ")}
                    </li>
                  ))}
              </ul>
            </div>
          </div>
        )}

      </section>

      {/* ================= TEAM RECOMMENDATION LINK ================= */}

      <div className="team-actions">
        <button
          className="secondary-button"
          onClick={() => navigate(`/tasks/${id}/recommendation`)}
        >
          <Users size={16} />
          Build a full team for this task
        </button>
      </div>

    </div>
  );
}
