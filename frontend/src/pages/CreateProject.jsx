import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Calendar, Sparkles } from "lucide-react";
import { createProject } from "../services/api";

/**
 * The option values below match the categories the model was trained
 * on. Sending lowercase values (as the old form did) meant the
 * one-hot encoder silently dropped them via handle_unknown="ignore".
 */
const DOMAINS = [
  "Banking", "E-commerce", "Education", "Energy", "FinTech",
  "Government", "Healthcare", "Insurance", "Logistics",
  "Manufacturing", "Media", "Retail",
];

const TYPES = [
  "AI/NLP", "API Development", "Automation", "Business Intelligence",
  "Cloud Migration", "Cybersecurity", "Dashboards", "Data Analytics",
  "Data Engineering", "Database Migration", "DevOps",
  "Digital Transformation",
];

const COMPLEXITY = ["Basic", "Moderate", "Advanced", "Critical"];
const CRITICALITY = ["Low", "Medium", "High", "Critical"];
const PRIORITY = ["Low", "Medium", "High", "Urgent"];

export default function CreateProject() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    project_id: "",
    project_name: "",
    project_domain: DOMAINS[0],
    project_type: TYPES[1],
    project_complexity: "Moderate",
    project_criticality: "Medium",
    priority: "Medium",
    start_date: "",
    end_date: "",
  });

  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const update = (event) => {
    const { name, value } = event.target;
    setForm((previous) => ({ ...previous, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError("");

    try {
      const payload = {
        project_name: form.project_name.trim(),
        project_domain: form.project_domain,
        project_type: form.project_type,
        project_complexity: form.project_complexity,
        project_criticality: form.project_criticality,
        priority: form.priority,
        start_date: form.start_date || null,
        end_date: form.end_date || null,
      };

      // project_id is optional; the backend generates PRJ000001 style
      // identifiers when it is omitted.
      if (form.project_id.trim()) {
        payload.project_id = form.project_id.trim();
      }

      const project = await createProject(payload);

      navigate(`/projects/${project.project_id}`);
    } catch (exception) {
      setError(exception.message || "Project could not be saved.");
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
    <div className="create-project-page">

      <button className="back-link" onClick={() => navigate("/projects")}>
        <ArrowLeft size={16} />
        Back to Projects
      </button>

      <div className="page-heading">
        <h1>Create New Project</h1>
        <p>
          These fields feed the model directly, so the options match the
          categories it was trained on.
        </p>
      </div>

      <form className="project-form-card" onSubmit={handleSubmit}>

        <div className="form-section-heading">
          <h2>Project Details</h2>
        </div>

        {error && <p className="form-error">{error}</p>}

        <div className="form-group">
          <label>Project Name <span>*</span></label>
          <input
            type="text"
            name="project_name"
            placeholder="e.g. Customer Data Platform"
            value={form.project_name}
            onChange={update}
            required
            maxLength={200}
          />
        </div>

        <div className="form-group">
          <label>Project ID</label>
          <input
            type="text"
            name="project_id"
            placeholder="Leave blank to generate automatically"
            value={form.project_id}
            onChange={update}
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Domain <span>*</span></label>
            {select("project_domain", DOMAINS)}
          </div>

          <div className="form-group">
            <label>Project Type <span>*</span></label>
            {select("project_type", TYPES)}
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
            <label>Priority <span>*</span></label>
            {select("priority", PRIORITY)}
          </div>

          <div className="form-group">
            <label>Start Date</label>
            <div className="date-wrapper">
              <input
                type="date"
                name="start_date"
                value={form.start_date}
                onChange={update}
              />
              <Calendar size={17} className="date-icon" />
            </div>
          </div>
        </div>

        <div className="form-group">
          <label>Deadline</label>
          <div className="date-wrapper">
            <input
              type="date"
              name="end_date"
              value={form.end_date}
              onChange={update}
            />
            <Calendar size={17} className="date-icon" />
          </div>
        </div>

        <div className="ai-info-box">
          <div className="ai-info-icon">
            <Sparkles size={19} />
          </div>

          <div>
            <h3>What happens next?</h3>
            <p>
              Add tasks to this project with their required skills. The
              model then scores every employee against each task.
            </p>
          </div>
        </div>

        <div className="form-actions">
          <button
            type="button"
            className="cancel-button"
            onClick={() => navigate("/projects")}
          >
            Cancel
          </button>

          <button type="submit" className="continue-button" disabled={saving}>
            {saving ? "Saving..." : "Create Project"}
          </button>
        </div>

      </form>

    </div>
  );
}
