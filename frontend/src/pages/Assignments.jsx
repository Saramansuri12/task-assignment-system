import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  cancelAssignment,
  completeAssignment,
  getAssignments,
  getEmployees,
  getTasks,
  updateAssignmentStatus,
} from "../services/api";
import { ClipboardCheck, Search } from "lucide-react";

const STATUSES = [
  "PENDING",
  "ACTIVE",
  "IN_PROGRESS",
  "COMPLETED",
  "CANCELLED",
  "REJECTED",
];

export default function Assignments() {
  const navigate = useNavigate();

  const [rows, setRows] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(null);

  const load = useCallback(() => {
    setLoading(true);
    setError("");

    return Promise.all([getAssignments(), getTasks(), getEmployees()])
      .then(([assignments, tasks, employees]) => {
        const taskById = new Map(
          tasks.map((task) => [task.task_id, task])
        );

        const employeeById = new Map(
          employees.map((employee) => [
            String(employee.employee_id),
            employee,
          ])
        );

        setRows(
          assignments.map((assignment) => ({
            ...assignment,
            taskTitle:
              taskById.get(assignment.task_id)?.task_title ||
              assignment.task_id,
            employeeName:
              employeeById.get(String(assignment.employee_id))?.name ||
              assignment.employee_id,
          }))
        );
      })
      .catch((exception) =>
        setError(exception.message || "Assignments could not be loaded.")
      )
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const run = async (assignmentId, action) => {
    setBusy(assignmentId);
    setError("");
    setMessage("");

    try {
      await action();
      setMessage(`Assignment ${assignmentId} updated.`);
      await load();
    } catch (exception) {
      setError(exception.message || "Update failed.");
    } finally {
      setBusy(null);
    }
  };

  const filtered = rows.filter((row) => {
    const text = search.toLowerCase();
    return (
      String(row.assignment_id).toLowerCase().includes(text) ||
      String(row.taskTitle).toLowerCase().includes(text) ||
      String(row.employeeName).toLowerCase().includes(text) ||
      String(row.status || "").toLowerCase().includes(text)
    );
  });

  return (
    <div className="task-management-page">

      <div className="task-management-header">
        <div>
          <p className="eyebrow">ASSIGNMENT MANAGEMENT</p>
          <h1>Assignments</h1>
          <p>Approve, progress, complete or cancel allocated work.</p>
        </div>
      </div>

      {loading && <p>Loading assignments...</p>}
      {error && <p className="form-error">{error}</p>}
      {message && <p className="form-success">{message}</p>}

      <div className="task-controls">
        <div className="task-search">
          <Search size={17} />
          <input
            type="text"
            placeholder="Search by task, employee, or status..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
      </div>

      <div className="task-table-card">

        <div className="task-table-header">
          <span>Assignment</span>
          <span>Task</span>
          <span>Employee</span>
          <span>Predicted</span>
          <span>Status</span>
          <span>Actions</span>
        </div>

        <div className="task-table-body">

          {filtered.length === 0 && !loading && (
            <div className="no-tasks-found">
              <ClipboardCheck size={30} />
              <h3>No assignments yet</h3>
              <p>Open a task and assign a recommended employee.</p>
            </div>
          )}

          {filtered.map((row) => (
            <div className="task-table-row" key={row.assignment_id}>

              <div className="task-title-cell">
                <strong>{row.assignment_id}</strong>
              </div>

              <div
                className="task-project clickable-row"
                onClick={() => navigate(`/tasks/${row.task_id}`)}
              >
                {row.taskTitle}
              </div>

              <div className="task-assignee">
                <span>{row.employeeName}</span>
              </div>

              <div>
                {row.success_probability != null
                  ? `${Math.round(row.success_probability * 100)}%`
                  : "-"}
              </div>

              <div>
                <select
                  value={row.status || "ACTIVE"}
                  disabled={busy === row.assignment_id}
                  onChange={(event) =>
                    run(row.assignment_id, () =>
                      updateAssignmentStatus(
                        row.assignment_id,
                        event.target.value
                      )
                    )
                  }
                >
                  {STATUSES.map((value) => (
                    <option key={value} value={value}>
                      {value}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <button
                  className="text-button"
                  disabled={busy === row.assignment_id}
                  onClick={() =>
                    run(row.assignment_id, () =>
                      completeAssignment(row.assignment_id)
                    )
                  }
                >
                  Complete
                </button>

                <button
                  className="text-button"
                  disabled={busy === row.assignment_id}
                  onClick={() =>
                    run(row.assignment_id, () =>
                      cancelAssignment(row.assignment_id)
                    )
                  }
                >
                  Cancel
                </button>
              </div>

            </div>
          ))}

        </div>

      </div>

    </div>
  );
}
