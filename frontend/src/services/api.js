const API_URL =
	import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export const API_BASE_URL = API_URL;

/**
 * Thrown for every non-2xx response so callers can react to the
 * specific status instead of only seeing a generic message.
 */
export class ApiError extends Error {
	constructor(status, message, detail) {
		super(message);
		this.name = "ApiError";
		this.status = status;
		this.detail = detail;
	}
}

function readDetail(payload) {
	if (!payload) return null;

	const detail = payload.detail ?? payload;

	if (typeof detail === "string") return detail;

	// FastAPI 422 validation errors arrive as an array.
	if (Array.isArray(detail)) {
		return detail
			.map((item) => item.msg || JSON.stringify(item))
			.join(", ");
	}

	if (typeof detail === "object") {
		if (detail.message) {
			const errors = Array.isArray(detail.errors)
				? ` (${detail.errors.join("; ")})`
				: "";
			return `${detail.message}${errors}`;
		}
		if (Array.isArray(detail.errors)) {
			return detail.errors.join("; ");
		}
		return JSON.stringify(detail);
	}

	return null;
}

const FRIENDLY = {
	400: "The request was rejected. Please check the values you entered.",
	401: "Your session has expired. Please sign in again.",
	403: "You do not have permission to do that.",
	404: "We could not find what you were looking for.",
	409: "That conflicts with something that already exists.",
	422: "Some fields are missing or invalid.",
	500: "The server ran into a problem. Please try again.",
};

export async function apiRequest(path, options = {}) {
	const token = localStorage.getItem("access_token");

	let response;

	try {
		response = await fetch(`${API_URL}${path}`, {
			...options,
			headers: {
				"Content-Type": "application/json",
				...(token ? { Authorization: `Bearer ${token}` } : {}),
				...options.headers,
			},
		});
	} catch {
		throw new ApiError(
			0,
			"Cannot reach the server. Check that the backend is running.",
			null
		);
	}

	if (!response.ok) {
		let payload = null;

		try {
			payload = await response.json();
		} catch {
			/* response had no JSON body */
		}

		const detail = readDetail(payload);

		if (response.status === 401) {
			localStorage.removeItem("access_token");
		}

		throw new ApiError(
			response.status,
			detail ||
				FRIENDLY[response.status] ||
				`Request failed (${response.status}).`,
			payload?.detail ?? null
		);
	}

	if (response.status === 204) return null;

	try {
		return await response.json();
	} catch {
		return null;
	}
}

/* ===================== AUTH ===================== */

export function login(username, password) {
	return apiRequest("/auth/login", {
		method: "POST",
		body: JSON.stringify({ username, password }),
	});
}

export function register(username, email, password, role = "MANAGER") {
	return apiRequest("/auth/register", {
		method: "POST",
		body: JSON.stringify({ username, email, password, role }),
	});
}

export function getCurrentUser() {
	return apiRequest("/auth/me");
}

export function logout() {
	localStorage.removeItem("access_token");
}

export function isAuthenticated() {
	return Boolean(localStorage.getItem("access_token"));
}

/* ===================== DASHBOARD ===================== */

export function getDashboardSummary() {
	return apiRequest("/dashboard/summary");
}

/* ===================== EMPLOYEES ===================== */

export function getEmployees() {
	return apiRequest("/employees/");
}

export function getEmployee(employeeId) {
	return apiRequest(`/employees/${encodeURIComponent(employeeId)}`);
}

export function getEmployeeSkills(employeeId) {
	return apiRequest(
		`/employee-skills/employee/${encodeURIComponent(employeeId)}`
	);
}

export function getEmployeeWorkload(employeeId) {
	return apiRequest(`/workload/employee/${encodeURIComponent(employeeId)}`);
}

export function getEmployeeAssignments(employeeId) {
	return apiRequest(
		`/assignments/employee/${encodeURIComponent(employeeId)}`
	);
}

/* ===================== SKILLS ===================== */

export function getSkills() {
	return apiRequest("/skills/");
}

/* ===================== PROJECTS ===================== */

export function getProjects() {
	return apiRequest("/projects/");
}

export function getProject(projectId) {
	return apiRequest(`/projects/${encodeURIComponent(projectId)}`);
}

export function createProject(project) {
	return apiRequest("/projects/", {
		method: "POST",
		body: JSON.stringify(project),
	});
}

/* ===================== TASKS ===================== */

// The router registers "" (no trailing slash) as the canonical path.
// Calling "/tasks/" produced a 307 redirect, which breaks CORS
// preflight in the browser.

export function getTasks() {
	return apiRequest("/tasks");
}

export function getTask(taskId) {
	return apiRequest(`/tasks/${encodeURIComponent(taskId)}`);
}

export function createTask(task) {
	return apiRequest("/tasks", {
		method: "POST",
		body: JSON.stringify(task),
	});
}

export function getTaskSkills(taskId) {
	return apiRequest(`/task-skills/task/${encodeURIComponent(taskId)}`);
}

/* ===================== RECOMMENDATIONS (ML) ===================== */

export function getAssignmentRecommendations(taskId, topK = 10) {
	return apiRequest(
		`/assignments/task/${encodeURIComponent(taskId)}/recommend?top_k=${topK}`
	);
}

export function getTeamRecommendation(taskId) {
	return apiRequest(
		`/assignments/task/${encodeURIComponent(taskId)}/recommend-team`
	);
}

export function validateAssignment(taskId, employeeId) {
	return apiRequest(
		`/assignments/validate/${encodeURIComponent(taskId)}/${encodeURIComponent(employeeId)}`
	);
}

/* ===================== ASSIGNMENTS ===================== */

export function getAssignments() {
	return apiRequest("/assignments");
}

export function getAssignment(assignmentId) {
	return apiRequest(`/assignments/${encodeURIComponent(assignmentId)}`);
}

export function getTaskAssignments(taskId) {
	return apiRequest(`/assignments/task/${encodeURIComponent(taskId)}`);
}

export function createAssignment(taskId, employeeId) {
	return apiRequest("/assignments", {
		method: "POST",
		body: JSON.stringify({ task_id: taskId, employee_id: employeeId }),
	});
}

export function getAssignmentHistory(assignmentId) {
	return apiRequest(
		`/assignments/${encodeURIComponent(assignmentId)}/history`
	);
}

export function updateAssignmentStatus(assignmentId, status) {
	return apiRequest(
		`/assignments/${encodeURIComponent(assignmentId)}/status`,
		{
			method: "PUT",
			body: JSON.stringify({ status }),
		}
	);
}

export function completeAssignment(assignmentId) {
	return apiRequest(
		`/assignments/${encodeURIComponent(assignmentId)}/complete`,
		{ method: "POST" }
	);
}

export function cancelAssignment(assignmentId) {
	return apiRequest(
		`/assignments/${encodeURIComponent(assignmentId)}/cancel`,
		{ method: "POST" }
	);
}
