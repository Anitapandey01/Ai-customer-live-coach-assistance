import { useState } from "react";

function Login({ onLogin, onRegister }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");

    if (!email.trim() || !password.trim()) {
      setError("Please enter your email and password.");
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/auth/login",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: email.trim(),
            password,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Invalid email or password."
        );
      }

      localStorage.setItem(
        "access_token",
        data.access_token
      );

      localStorage.setItem(
        "user",
        JSON.stringify({
          user_id: data.user_id,
          name: data.name,
          email: data.email,
          role: data.role,
        })
      );

      onLogin({
        user_id: data.user_id,
        name: data.name,
        email: data.email,
        role: data.role,
        access_token: data.access_token,
      });
    } catch (error) {
      setError(
        error.message ||
        "Unable to connect to the server."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="brand-section">
          <div className="brand-icon">AI</div>

          <h1>SupportAI</h1>

          <p>
            AI-Powered Customer Support Assistant
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="login-form"
        >
          <div className="form-group">
            <label htmlFor="email">
              Email
            </label>

            <input
              id="email"
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">
              Password
            </label>

            <input
              id="password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              required
            />
          </div>

          {error && (
            <p className="login-error">
              {error}
            </p>
          )}

          <button
            type="submit"
            className="primary-button full-width"
            disabled={isLoading}
          >
            {isLoading
              ? "Logging in..."
              : "Login"}
          </button>
        </form>

        <p className="login-note">
          Don't have an account?{" "}
          <button
            type="button"
            className="text-button"
            onClick={onRegister}
          >
            Create Account
          </button>
        </p>
      </div>
    </div>
  );
}

export default Login;