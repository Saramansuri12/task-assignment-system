import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Lock, Mail, Sparkles, User } from "lucide-react";
import { register } from "../services/api";

export default function Signup() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const update = (event) => {
    setForm({ ...form, [event.target.name]: event.target.value });
  };

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await register(form.username, form.email, form.password, "EMPLOYEE");
      navigate("/login", { state: { registered: true } });
    } catch {
      setError("Registration failed. The username or email may already exist.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-brand">
        <div className="login-brand-content">
          <div className="login-logo"><Sparkles size={20} /></div>
          <p className="login-eyebrow">AI-POWERED WORKFORCE OPTIMIZATION</p>
          <h1>Build a smarter way to assign work.</h1>
          <p className="login-brand-description">
            Create an account to manage teams, projects, and explainable AI recommendations.
          </p>
        </div>
      </div>

      <div className="login-form-section">
        <div className="login-form-wrapper">
          <div className="login-mobile-logo">
            <div className="login-logo"><Sparkles size={18} /></div>
            <span>Task Assignment System</span>
          </div>

          <div className="login-heading">
            <p className="login-form-eyebrow">CREATE ACCOUNT</p>
            <h2>Get started</h2>
            <p>Create your account to access the workforce dashboard.</p>
          </div>

          <form onSubmit={submit}>
            {error && <p className="form-error">{error}</p>}

            <div className="login-field">
              <label htmlFor="username">Username</label>
              <div className="login-input-wrapper">
                <User size={17} />
                <input id="username" name="username" value={form.username} onChange={update} required />
              </div>
            </div>

            <div className="login-field">
              <label htmlFor="email">Email address</label>
              <div className="login-input-wrapper">
                <Mail size={17} />
                <input id="email" name="email" type="email" value={form.email} onChange={update} required />
              </div>
            </div>

            <div className="login-field">
              <label htmlFor="password">Password</label>
              <div className="login-input-wrapper">
                <Lock size={17} />
                <input id="password" name="password" type="password" value={form.password} onChange={update} minLength={8} required />
              </div>
            </div>

            <button type="submit" className="login-submit" disabled={loading}>
              {loading ? "Creating account..." : "Create Account"}
            </button>
          </form>

          <p className="auth-switch">
            Already have an account?{" "}
            <button type="button" onClick={() => navigate("/login")}>Sign in</button>
          </p>
        </div>
      </div>
    </div>
  );
}