import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getAssignments, getEmployees, getTasks } from "../services/api";
import {
  Search,
  Plus,
  CheckCircle2,
  Clock,
  AlertCircle,
  ListTodo,
} from "lucide-react";

export default function TaskManagement() {
  const [search, setSearch] = useState("");
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const load = useCallback(() => {
    setLoading(true);
    setError("");

    return Promise.all([getTasks(), getAssignments(), getEmployees()])
      .then(([taskRecords, assignments, employees]) => {
        const employeeById = new Map(
          employees.map((employee) => [
            String(employee.employee_id),
            employee,
          ])
        );

        const assignmentsByTask = new Map();

        assignments.forEach((assignment) => {
          const list = assignmentsByTask.get(assignment.task_id) || [];
          list.push(assignment);
          assignmentsByTask.set(assignment.task_id, list);
        });

        setTasks(
          taskRecords.map((task) => {
            const taskAssignments = assignmentsByTask.get(task.task_id) || [];
            const first = taskAssignments[0];

            const assigneeName = first
              ? employeeById.get(String(first.employee_id))?.name ||
                first.employee_id
              : "Unassigned";

            // Task status is derived from its assignments, since the
            // tasks table has no status column.
            let status = "Unassigned";

            if (taskAssignments.length) {
              const statuses = taskAssignments.map((item) =>
                (item.status || "").toUpperCase()
              );

              if (statuses.every((value) => value === "COMPLETED")) {
                status = "Completed";
              } else if (statuses.some((value) => value === "IN_PROGRESS")) {
                status = "In Progress";
              } else if (statuses.some((value) => value === "PENDING")) {
                status = "Pending";
              } else {
                status = "Assigned";
              }
            }

            return {
              id: task.task_id,
              title: task.task_title || task.task_id,
              project: task.project_id,
              assignee: assigneeName,
              assigneeCount: taskAssignments.length,
              initials:
                assigneeName === "Unassigned"
                  ? "--"
                  : assigneeName.slice(0, 2).toUpperCase(),
              priority: task.priority || "Medium",
              status,
              deadline: task.task_due_date || "No deadline",
            };
          })
        );
      })
      .catch((exception) =>
        setError(exception.message || "Task data could not be loaded.")
      )
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const filteredTasks = tasks.filter((task) => {
    const searchText = search.toLowerCase();

    return (
      task.title.toLowerCase().includes(searchText) ||
      String(task.project).toLowerCase().includes(searchText) ||
      String(task.id).toLowerCase().includes(searchText) ||
      task.assignee.toLowerCase().includes(searchText)
    );
  });

  const countBy = (value) =>
    tasks.filter((task) => task.status === value).length;

  return (
    <div className="task-management-page">

      {/* ================= HEADER ================= */}

      <div className="task-management-header">
        <div>
          <p className="eyebrow">TASK MANAGEMENT</p>
          <h1>Tasks</h1>
          <p>
            Open a task to request model-driven recommendations and create
            an assignment.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={() => navigate("/tasks/new")}
        >
          <Plus size={16} />
          Create Task
        </button>
      </div>

      {loading && <p>Loading tasks...</p>}

      {error && (
        <div className="form-error">
          {error}{" "}
          <button type="button" className="text-button" onClick={load}>
            Retry
          </button>
        </div>
      )}

      {/* ================= TASK STATS ================= */}

      <div className="task-stats-grid">

        <div className="task-stat-card">
          <ListTodo size={19} />
          <div>
            <span>Total Tasks</span>
            <strong>{tasks.length}</strong>
          </div>
        </div>

        <div className="task-stat-card completed">
          <CheckCircle2 size={19} />
          <div>
            <span>Completed</span>
            <strong>{countBy("Completed")}</strong>
          </div>
        </div>

        <div className="task-stat-card progress">
          <Clock size={19} />
          <div>
            <span>In Progress</span>
            <strong>{countBy("In Progress")}</strong>
          </div>
        </div>

        <div className="task-stat-card pending">
          <AlertCircle size={19} />
          <div>
            <span>Unassigned</span>
            <strong>{countBy("Unassigned")}</strong>
          </div>
        </div>

      </div>

      {/* ================= SEARCH ================= */}

      <div className="task-controls">
        <div className="task-search">
          <Search size={17} />

          <input
            type="text"
            placeholder="Search tasks, projects, or employees..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
      </div>

      {/* ================= TASK TABLE ================= */}

      <div className="task-table-card">

        <div className="task-table-header">
          <span>Task</span>
          <span>Project</span>
          <span>Assignee</span>
          <span>Priority</span>
          <span>Status</span>
          <span>Deadline</span>
        </div>

        <div className="task-table-body">

          {filteredTasks.length > 0 ? (
            filteredTasks.map((task) => (
              <div
                className="task-table-row clickable-task-row"
                key={task.id}
                onClick={() => navigate(`/tasks/${task.id}`)}
              >

                <div className="task-title-cell">
                  <div className="task-icon">
                    {task.status === "Completed" ? (
                      <CheckCircle2 size={16} />
                    ) : (
                      <Clock size={16} />
                    )}
                  </div>

                  <strong>{task.title}</strong>
                </div>

                <div className="task-project">{task.project}</div>

                <div className="task-assignee">
                  <div className="task-avatar">{task.initials}</div>

                  <span>
                    {task.assignee}
                    {task.assigneeCount > 1
                      ? ` +${task.assigneeCount - 1}`
                      : ""}
                  </span>
                </div>

                <div>
                  <span
                    className={`priority-badge ${String(
                      task.priority
                    ).toLowerCase()}`}
                  >
                    {task.priority}
                  </span>
                </div>

                <div>
                  <span
                    className={`task-status-badge ${task.status
                      .toLowerCase()
                      .replaceAll(" ", "-")}`}
                  >
                    {task.status}
                  </span>
                </div>

                <div className="task-deadline">{task.deadline}</div>

              </div>
            ))
          ) : (
            !loading && (
              <div className="no-tasks-found">
                <ListTodo size={30} />
                <h3>No tasks found</h3>
                <p>
                  {tasks.length === 0
                    ? "Create a task to get started."
                    : "Try different search keywords."}
                </p>
              </div>
            )
          )}

        </div>

      </div>

    </div>
  );
}
