import { useEffect, useState } from "react";
import { FolderKanban, Plus } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { getProjects } from "../services/api";

export default function Projects() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getProjects()
      .then(setProjects)
      .catch(() => setError("Projects could not be loaded."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <p className="eyebrow">PROJECT MANAGEMENT</p>
          <h1>Projects</h1>
          <p className="dashboard-description">Manage projects and their assigned work.</p>
        </div>
        <button className="primary-button" onClick={() => navigate("/projects/new")}>
          <Plus size={17} /> Create Project
        </button>
      </div>

      {loading && <p>Loading projects...</p>}
      {error && <p className="form-error">{error}</p>}
      {!loading && !error && projects.length === 0 && <p>No projects found.</p>}

      <div className="project-list">
        {projects.map((project) => (
          <button
            className="project-row"
            key={project.project_id}
            onClick={() => navigate(`/projects/${project.project_id}`)}
          >
            <div className="project-main">
              <div className="project-icon"><FolderKanban size={19} /></div>
              <div>
                <h3>{project.project_name || project.project_domain || project.project_id}</h3>
                <div className="project-meta">
                  <span>{project.project_type || "Project"}</span>
                  <span>Priority: {project.priority || "Not set"}</span>
                </div>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
