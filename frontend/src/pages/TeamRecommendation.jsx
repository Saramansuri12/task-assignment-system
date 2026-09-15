import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  createAssignment,
  getTask,
  getTaskAssignments,
  getTeamRecommendation,
} from "../services/api";
import {
  ArrowLeft,
  Sparkles,
  CheckCircle2,
  Users,
  Clock,
  AlertCircle,
} from "lucide-react";

export default function TeamRecommendation() {
  const navigate = useNavigate();
  const { id } = useParams();

  const [task, setTask] = useState(null);
  const [result, setResult] = useState(null);
  const [assignedIds, setAssignedIds] = useState(new Set());

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [approving, setApproving] = useState(false);
  const [message, setMessage] = useState("");

  const load = useCallback(() => {
    if (!id) return Promise.resolve();

    setLoading(true);
    setError("");

    return Promise.all([
      getTask(id),
      getTeamRecommendation(id),
      getTaskAssignments(id),
    ])
      .then(([taskResult, teamResult, assignments]) => {
        setTask(taskResult);
        setResult(teamResult);
        setAssignedIds(
          new Set(assignments.map((item) => String(item.employee_id)))
        );
      })
      .catch((exception) =>
        setError(
          exception.message || "Team recommendation could not be generated."
        )
      )
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  /**
   * Creates a real assignment for every recommended member that is not
   * already assigned. Previously this button only navigated away
   * without persisting anything.
   */
  const approveTeam = async () => {
    if (!result?.team?.length) return;

    setApproving(true);
    setError("");
    setMessage("");

    const created = [];
    const failed = [];

    for (const member of result.team) {
      if (assignedIds.has(String(member.employee_id))) continue;

      try {
        await createAssignment(id, member.employee_id);
        created.push(member.employee_id);
      } catch (exception) {
        failed.push(`${member.employee_id}: ${exception.message}`);
      }
    }

    setApproving(false);

    if (created.length) {
      setMessage(`Assigned ${created.join(", ")} to this task.`);
    }

    if (failed.length) {
      setError(failed.join(" | "));
    }

    await load();
  };

  if (loading) {
    return (
      <div className="team-recommendation-page">
        <p>Building the recommended team...</p>
      </div>
    );
  }

  return (
    <div className="team-recommendation-page">

      <button
        className="back-link"
        onClick={() => navigate(`/tasks/${id}`)}
      >
        <ArrowLeft size={16} />
        Back to Task
      </button>

      <div className="team-match-heading">
        <div>
          <p className="eyebrow">TEAM RECOMMENDATION</p>
          <h1>{task?.task_title || id}</h1>
          <p>
            Members are picked greedily by predicted success score and how
            much new required-skill coverage each one adds.
          </p>
        </div>

        {result && (
          <div className="recommendation-badge">
            <Sparkles size={15} />
            {result.scoring_method === "ml_model"
              ? "ML model"
              : "Rule-based fallback"}
          </div>
        )}
      </div>

      {error && <p className="form-error">{error}</p>}
      {message && <p className="form-success">{message}</p>}

      {result && (
        <>
          <div className="match-summary">
            <div className="match-score-box">
              <div className="match-score">{result.skill_coverage}%</div>

              <div>
                <h3>Skill Coverage</h3>
                <p>{result.recommendation_reason}</p>
              </div>
            </div>

            <div className="match-summary-info">
              <div>
                <Users size={18} />
                <span>Team Size</span>
                <strong>
                  {result.team.length} / {result.required_team_size}
                </strong>
              </div>

              <div>
                <CheckCircle2 size={18} />
                <span>Covered Skills</span>
                <strong>{result.covered_skills.length}</strong>
              </div>

              <div>
                <AlertCircle size={18} />
                <span>Uncovered Critical</span>
                <strong>{result.uncovered_critical_skills.length}</strong>
              </div>
            </div>
          </div>

          <div className="team-recommendation-layout">

            <div className="recommended-team-section">

              <div className="team-section-header">
                <div>
                  <h2>Recommended Team Members</h2>
                  <p>Ranked by predicted success and skill contribution</p>
                </div>

                <span className="team-count">
                  {result.team.length} selected
                </span>
              </div>

              <div className="recommended-members">
                {result.team.length === 0 && (
                  <p>No eligible team could be formed for this task.</p>
                )}

                {result.team.map((member) => (
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
                        <span>Predicted success</span>
                        <strong>{member.score}%</strong>
                      </div>
                    </div>

                    <div className="member-details">
                      <div>
                        <CheckCircle2 size={14} />
                        <span>{member.skill_match_pct}% skill match</span>
                      </div>

                      <div>
                        <Clock size={14} />
                        <span>
                          {member.current_workload_pct ?? 0}% workload
                        </span>
                      </div>
                    </div>

                    <div className="member-skills">
                      {member.matched_skills.length === 0 ? (
                        <span>Adds no new required skills</span>
                      ) : (
                        member.matched_skills.map((skill) => (
                          <span key={skill}>{skill}</span>
                        ))
                      )}
                    </div>

                    <div className="ai-reason">
                      <Sparkles size={14} />
                      <div>
                        <strong>Why this member</strong>
                        <p>{member.reason}</p>
                      </div>
                    </div>

                    {assignedIds.has(String(member.employee_id)) && (
                      <p className="form-success">Already assigned</p>
                    )}

                  </div>
                ))}
              </div>

            </div>

            <aside className="team-sidebar">

              <div className="team-sidebar-card">
                <h2>Covered Skills</h2>

                <div className="required-skills-list">
                  {result.covered_skills.length === 0 && <p>None yet.</p>}

                  {result.covered_skills.map((skill) => (
                    <div className="required-skill-item" key={skill}>
                      <CheckCircle2 size={14} />
                      <span>{skill}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="team-sidebar-card">
                <h2>Uncovered Skills</h2>

                <div className="required-skills-list">
                  {result.uncovered_skills.length === 0 ? (
                    <p>Every required skill is covered.</p>
                  ) : (
                    result.uncovered_skills.map((skill) => (
                      <div className="required-skill-item" key={skill}>
                        <AlertCircle size={14} />
                        <span>
                          {skill}
                          {result.uncovered_critical_skills.includes(skill)
                            ? " (critical)"
                            : ""}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </div>

            </aside>

          </div>

          <div className="team-actions">
            <button
              className="cancel-button"
              onClick={() => navigate(`/tasks/${id}`)}
            >
              Back
            </button>

            <button
              className="approve-team-button"
              onClick={approveTeam}
              disabled={approving || result.team.length === 0}
            >
              {approving
                ? "Creating assignments..."
                : "Approve & Assign Team"}
            </button>
          </div>
        </>
      )}

    </div>
  );
}
