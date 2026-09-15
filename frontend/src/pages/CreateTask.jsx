import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Plus, X, Calendar, Sparkles } from "lucide-react";
import { createTask, getProjects, getSkills } from "../services/api";

const COMPLEXITY = ["Basic", "Moderate", "Advanced", "Critical"];
const CRITICALITY = ["Low", "Medium", "High", "Critical"];
const PRIORITY = ["Low", "Medium", "High", "Urgent"];

const ROLES = [
  "Backend Developer", "BI Developer", "Business Analyst",
  "Cloud Engineer", "Compliance Specialist", "Data Analyst",
  "Data Engineer", "Data Scientist", "Database Administrator",
  "Delivery Manager", "DevOps Engineer", "Enterprise Architect",
];

export default function CreateTask() {
  const navigate = useNavigate();

  const [projects, setProjects] = useState([]);
  const [availableSkills, setAvailableSkills] = useState([]);

  const [form, setForm] = useState({
    task_id: "",
    project_id: "",
    task_title: "",
    task_description: "",
    project_complexity: "Moderate",
    project_criticality: "Medium",
    priority: "Medium",
    role_required: ROLES[0],
    team_size_required: 1,
    estimated_hours: "",
    deadline_days: "",
    required_experience_years: "",
    task_start_date: "",
    task_due_date: "",
  });

  const [skills, setSkills] = useState([]);
  const [skillInput, setSkillInput] = useState("");
  const [skillLevel, setSkillLevel] = useState(3);
  const [skillCritical, setSkillCritical] = useState(false);

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getProjects()
      .then((records) => {
        setProjects(records);
        if (records.length) {
          setForm((previous) => ({
            ...previous,
            project_id: previous.project_id || records[0].project_id,
          }));
        }
      })
      .catch(() => setProjects([]));

    getSkills()
      .then(setAvailableSkills)
      .catch(() => setAvailableSkills([]));
  }, []);

  const update = (event) => {
    const { name, value } = event.target;
    setForm((previous) => ({ ...previous, [name]: value }));
  };

  const addSkill = () => {
    const name = skillInput.trim();
    if (!name) return;

    if (skills.some((skill) => skill.skill_name === name)) {
      setSkillInput("");
      return;
    }

    // Reuse an existing skill record when the name matches, so the
    // task links to the same skill_id employees already have.
    const existing = availableSkills.find(
      (skill) =>
        (skill.skill_name || "").toLowerCase() === name.toLowerCase()
    );

    setSkills([
      ...skills,
      {
        skill_id: existing?.skill_id || null,
        skill_name: existing?.skill_name || name,
        required_level: Number(skillLevel),
        is_critical: skillCritical,
      },
    ]);

    setSkillInput("");
    setSkillCritical(false);
  };

  const removeSkill = (name) => {
    setSkills(skills.filter((skill) => skill.skill_name !== name));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError("");

    try {
      const number = (value) =>
        value === "" || value === null ? undefined : Number(value);

      const payload = {
        project_id: form.project_id,
        task_title: form.task_title,
        task_description: form.task_description || undefined,
        project_complexity: form.project_complexity,
        project_criticality: form.project_criticality,
        priority: form.priority,
        role_required: form.role_required,
        team_size_required: number(form.team_size_required) || 1,
        estimated_hours: number(form.estimated_hours),
        deadline_days: number(form.deadline_days),
        required_experience_years: number(form.required_experience_years),
        task_start_date: form.task_start_date || undefined,
        task_due_date: form.task_due_date || undefined,
        // Persisted as task_skills rows so the model has real
        // requirements to match against.
        required_skills: skills,
      };

      if (form.task_id.trim()) {
        payload.task_id = form.task_id.trim();
      }

      const task = await createTask(payload);

      navigate(`/tasks/${task.task_id}`);
    } catch (exception) {
      setError(exception.message || "Task could not be created.");
    } finally {
      setSaving(false);
    }
  };

  const select = (name, options) => (
    <select name={name} value={form[name]} onChange={update} required>
      {options.map((option) => (
        <option key={option} value={option}>
          {option}
        </option>
      ))}
    </select>
  );

  return (
    <div className="create-task-page">

      <button className="create-task-back" onClick={() => navigate("/tasks")}>
        <ArrowLeft size={16} />
        Back to Tasks
      </button>

      <div className="create-task-header">
        <div>
          <p className="eyebrow">TASK MANAGEMENT</p>
          <h1>Create New Task</h1>
          <p>
            Define the requirements. The model uses every field below to
            score candidates.
          </p>
        </div>
      </div>

      <form className="create-task-form" onSubmit={handleSubmit}>

        <section className="create-task-card">

          {error && <p className="form-error">{error}</p>}

          {projects.length === 0 && (
            <p className="form-error">
              No projects exist yet. Create a project first.
            </p>
          )}

          <div className="form-group">
            <label>Task ID</label>
            <input
              type="text"
              name="task_id"
              placeholder="Leave blank to generate automatically"
              value={form.task_id}
              onChange={update}
            />
          </div>

          <div className="form-group">
            <label>Project <span>*</span></label>
            <select
              name="project_id"
              value={form.project_id}
              onChange={update}
              required
            >
              <option value="">Select a project</option>
              {projects.map((project) => (
                <option key={project.project_id} value={project.project_id}>
                  {project.project_name || project.project_domain || project.project_id} (
                  {project.project_id})
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Task Title <span>*</span></label>
            <input
              type="text"
              name="task_title"
              value={form.task_title}
              onChange={update}
              required
            />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              name="task_description"
              rows="4"
              value={form.task_description}
              onChange={update}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Role Required <span>*</span></label>
              {select("role_required", ROLES)}
            </div>

            <div className="form-group">
              <label>Priority <span>*</span></label>
              {select("priority", PRIORITY)}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Complexity <span>*</span></label>
              {select("project_complexity", COMPLEXITY)}
            </div>

            <div className="form-group">
              <label>Criticality <span>*</span></label>
              {select("project_criticality", CRITICALITY)}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Team Size Required</label>
              <input
                type="number"
                name="team_size_required"
                min="1"
                value={form.team_size_required}
                onChange={update}
              />
            </div>

            <div className="form-group">
              <label>Estimated Hours</label>
              <input
                type="number"
                name="estimated_hours"
                min="1"
                value={form.estimated_hours}
                onChange={update}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Deadline (days)</label>
              <input
                type="number"
                name="deadline_days"
                min="0"
                value={form.deadline_days}
                onChange={update}
              />
            </div>

            <div className="form-group">
              <label>Required Experience (years)</label>
              <input
                type="number"
                name="required_experience_years"
                min="0"
                step="0.5"
                value={form.required_experience_years}
                onChange={update}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Start Date</label>
              <div className="date-wrapper">
                <input
                  type="date"
                  name="task_start_date"
                  value={form.task_start_date}
                  onChange={update}
                />
                <Calendar size={17} className="date-icon" />
              </div>
            </div>

            <div className="form-group">
              <label>Due Date</label>
              <div className="date-wrapper">
                <input
                  type="date"
                  name="task_due_date"
                  value={form.task_due_date}
                  onChange={update}
                />
                <Calendar size={17} className="date-icon" />
              </div>
            </div>
          </div>

        </section>

        {/* ================= REQUIRED SKILLS ================= */}

        <section className="create-task-card">

          <div className="create-task-card-header">
            <div>
              <h2>Required Skills</h2>
              <p>
                Skill matching drives most of the model's score. Mark the
                must-haves as critical.
              </p>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Skill</label>
              <input
                type="text"
                list="skill-options"
                placeholder="e.g. Python"
                value={skillInput}
                onChange={(event) => setSkillInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    addSkill();
                  }
                }}
              />

              <datalist id="skill-options">
                {availableSkills.slice(0, 300).map((skill) => (
                  <option key={skill.skill_id} value={skill.skill_name || ""} />
                ))}
              </datalist>
            </div>

            <div className="form-group">
              <label>Required Level</label>
              <input
                type="number"
                min="1"
                max="5"
                value={skillLevel}
                onChange={(event) => setSkillLevel(event.target.value)}
              />
            </div>

            <div className="form-group">
              <label>
                <input
                  type="checkbox"
                  checked={skillCritical}
                  onChange={(event) => setSkillCritical(event.target.checked)}
                />{" "}
                Critical
              </label>

              <button type="button" className="add-button" onClick={addSkill}>
                <Plus size={14} />
                Add
              </button>
            </div>
          </div>

          <div className="technology-tags">
            {skills.length === 0 && (
              <p>No skills added yet.</p>
            )}

            {skills.map((skill) => (
              <span className="technology-tag" key={skill.skill_name}>
                {skill.skill_name} · L{skill.required_level}
                {skill.is_critical ? " · critical" : ""}
                <button
                  type="button"
                  onClick={() => removeSkill(skill.skill_name)}
                >
                  <X size={12} />
                </button>
              </span>
            ))}
          </div>

        </section>

        <div className="ai-info-box">
          <div className="ai-info-icon">
            <Sparkles size={19} />
          </div>

          <div>
            <h3>What happens next?</h3>
            <p>
              After saving you land on the task page, where you can run the
              model and assign the recommended employees.
            </p>
          </div>
        </div>

        <div className="form-actions">
          <button
            type="button"
            className="cancel-button"
            onClick={() => navigate("/tasks")}
          >
            Cancel
          </button>

          <button
            type="submit"
            className="continue-button"
            disabled={saving || !form.project_id}
          >
            {saving ? "Creating..." : "Create Task"}
          </button>
        </div>

      </form>

    </div>
  );
}
