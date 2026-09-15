import {
  LayoutDashboard,
  FolderKanban,
  Users,
  ListTodo,
  ClipboardCheck,
  LogOut,
  Sparkles,
} from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { getCurrentUser, logout } from "../services/api";

export default function Sidebar() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .catch(() => setUser(null));
  }, []);

  const links = [
    { name: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
    { name: "Projects", path: "/projects", icon: FolderKanban },
    { name: "Tasks", path: "/tasks", icon: ListTodo },
    { name: "Assignments", path: "/assignments", icon: ClipboardCheck },
    { name: "Team", path: "/team", icon: Users },
  ];

  const displayName = user?.username || "Signed in";
  const displayRole = user?.role || "";

  const initials = displayName.slice(0, 2).toUpperCase();

  const handleLogout = () => {
    // Previously this only navigated to /login without clearing the
    // token, so the guard immediately redirected back in.
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon">
          <Sparkles size={20} />
        </div>

        <div>
          <div className="logo-title">Task Assignment AI</div>
          <div className="logo-subtitle">Intelligent Team Allocation</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {links.map((link) => {
          const Icon = link.icon;

          return (
            <NavLink
              key={link.path}
              to={link.path}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? "active" : ""}`
              }
            >
              <Icon size={19} />
              <span>{link.name}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="sidebar-bottom">
        <div className="profile">
          <div className="profile-avatar">{initials}</div>

          <div className="profile-info">
            <div className="profile-name">{displayName}</div>
            <div className="profile-role">{displayRole}</div>
          </div>

          <button
            className="logout-button"
            onClick={handleLogout}
            title="Sign out"
          >
            <LogOut size={17} />
          </button>
        </div>
      </div>
    </aside>
  );
}
