import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useLocation,
} from "react-router-dom";

import Layout from "./components/Layout";

import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import TeamManagement from "./pages/TeamManagement";
import EmployeeDetails from "./pages/EmployeeDetails";

import CreateProject from "./pages/CreateProject";
import RequirementsReview from "./pages/RequirementsReview";
import TeamRecommendation from "./pages/TeamRecommendation";
import ProjectDetails from "./pages/ProjectDetails";
import Projects from "./pages/Projects";

import TaskManagement from "./pages/TaskManagement";
import TaskDetails from "./pages/TaskDetails";
import CreateTask from "./pages/CreateTask";

import Assignments from "./pages/Assignments";

/**
 * Guards a single route. The previous version wrapped <Routes> as a
 * whole and only whitelisted "/login", so visiting "/signup" without a
 * token bounced straight back to login and no account could ever be
 * created.
 */
function ProtectedRoute({ children }) {
  const location = useLocation();

  if (!localStorage.getItem("access_token")) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Layout>{children}</Layout>;
}

/** Sends already-signed-in users straight to the dashboard. */
function PublicOnlyRoute({ children }) {
  if (localStorage.getItem("access_token")) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

function NotFound() {
  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <p className="eyebrow">404</p>
          <h1>Page not found</h1>
          <p className="dashboard-description">
            That page does not exist. Use the sidebar to get back on track.
          </p>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* ================= PUBLIC ================= */}

        <Route
          path="/login"
          element={
            <PublicOnlyRoute>
              <Login />
            </PublicOnlyRoute>
          }
        />

        <Route
          path="/signup"
          element={
            <PublicOnlyRoute>
              <Signup />
            </PublicOnlyRoute>
          }
        />

        {/* ================= DASHBOARD ================= */}

        <Route
          path="/"
          element={<Navigate to="/dashboard" replace />}
        />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* ================= TEAM ================= */}

        <Route
          path="/team"
          element={
            <ProtectedRoute>
              <TeamManagement />
            </ProtectedRoute>
          }
        />

        <Route
          path="/team/:id"
          element={
            <ProtectedRoute>
              <EmployeeDetails />
            </ProtectedRoute>
          }
        />

        {/* ================= PROJECTS ================= */}

        <Route
          path="/projects"
          element={
            <ProtectedRoute>
              <Projects />
            </ProtectedRoute>
          }
        />

        <Route
          path="/projects/new"
          element={
            <ProtectedRoute>
              <CreateProject />
            </ProtectedRoute>
          }
        />

        <Route
          path="/projects/:id/requirements"
          element={
            <ProtectedRoute>
              <RequirementsReview />
            </ProtectedRoute>
          }
        />

        <Route
          path="/projects/:id"
          element={
            <ProtectedRoute>
              <ProjectDetails />
            </ProtectedRoute>
          }
        />

        {/* ================= TASKS ================= */}

        <Route
          path="/tasks"
          element={
            <ProtectedRoute>
              <TaskManagement />
            </ProtectedRoute>
          }
        />

        <Route
          path="/tasks/new"
          element={
            <ProtectedRoute>
              <CreateTask />
            </ProtectedRoute>
          }
        />

        <Route
          path="/tasks/:id/recommendation"
          element={
            <ProtectedRoute>
              <TeamRecommendation />
            </ProtectedRoute>
          }
        />

        <Route
          path="/tasks/:id"
          element={
            <ProtectedRoute>
              <TaskDetails />
            </ProtectedRoute>
          }
        />

        {/* ================= ASSIGNMENTS ================= */}

        <Route
          path="/assignments"
          element={
            <ProtectedRoute>
              <Assignments />
            </ProtectedRoute>
          }
        />

        <Route path="*" element={<NotFound />} />

      </Routes>
    </BrowserRouter>
  );
}

export default App;
