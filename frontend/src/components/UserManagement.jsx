import { useEffect, useState } from "react";

function UserManagement({ user, onBack }) {
  const [users, setUsers] = useState([]);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("employee");

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const token = user?.access_token;

  const fetchUsers = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/users/",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to load users."
        );
      }

      setUsers(data.users || []);
    } catch (error) {
      setError(
        error.message || "Unable to load users."
      );
    }
  };

  useEffect(() => {
    if (user?.role === "admin") {
      fetchUsers();
    }
  }, [user]);

  const handleCreateUser = async (event) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    const trimmedName = name.trim();
    const trimmedEmail = email.trim().toLowerCase();

    if (
      !trimmedName ||
      !trimmedEmail ||
      !password
    ) {
      setError("Please fill in all fields.");
      return;
    }

    if (password.length < 8) {
      setError(
        "Password must be at least 8 characters long."
      );
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/users/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            name: trimmedName,
            email: trimmedEmail,
            password,
            role,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to create user."
        );
      }

      setSuccess(
        `${role === "admin" ? "Admin" : "Employee"} account created successfully.`
      );

      setName("");
      setEmail("");
      setPassword("");
      setRole("employee");

      await fetchUsers();
    } catch (error) {
      setError(
        error.message || "Unable to create user."
      );
    } finally {
      setIsLoading(false);
    }
  };

  if (user?.role !== "admin") {
    return (
      <div className="mode-container">
        <h2>Access Denied</h2>

        <p>
          Only administrators can access User Management.
        </p>

        <button
          type="button"
          className="secondary-button"
          onClick={onBack}
        >
          Back
        </button>
      </div>
    );
  }

  return (
    <div className="mode-container">
      <div className="mode-header">
        <div>
          <h2>User Management</h2>
          <p>
            Create and view administrator and employee accounts.
          </p>
        </div>

        <button
          type="button"
          className="secondary-button"
          onClick={onBack}
        >
          Back
        </button>
      </div>

      <div className="user-management-grid">
        <div className="user-form-card">
          <h3>Create User</h3>

          <form onSubmit={handleCreateUser}>
            <div className="form-group">
              <label htmlFor="user-name">
                Full Name
              </label>

              <input
                id="user-name"
                type="text"
                placeholder="Enter full name"
                value={name}
                onChange={(event) =>
                  setName(event.target.value)
                }
              />
            </div>

            <div className="form-group">
              <label htmlFor="user-email">
                Email
              </label>

              <input
                id="user-email"
                type="email"
                placeholder="Enter email"
                value={email}
                onChange={(event) =>
                  setEmail(event.target.value)
                }
              />
            </div>

            <div className="form-group">
              <label htmlFor="user-password">
                Temporary Password
              </label>

              <input
                id="user-password"
                type="password"
                placeholder="Minimum 8 characters"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
              />
            </div>

            <div className="form-group">
              <label htmlFor="user-role">
                Role
              </label>

              <select
                id="user-role"
                value={role}
                onChange={(event) =>
                  setRole(event.target.value)
                }
              >
                <option value="employee">
                  Employee
                </option>

                <option value="admin">
                  Admin
                </option>
              </select>
            </div>

            {error && (
              <p className="login-error">
                {error}
              </p>
            )}

            {success && (
              <p className="login-success">
                {success}
              </p>
            )}

            <button
              type="submit"
              className="primary-button"
              disabled={isLoading}
            >
              {isLoading
                ? "Creating..."
                : "Create User"}
            </button>
          </form>
        </div>

        <div className="users-list-card">
          <h3>Registered Users</h3>

          {users.length === 0 ? (
            <p>No users found.</p>
          ) : (
            <div className="users-list">
              {users.map((item) => (
                <div
                  key={item.user_id}
                  className="user-row"
                >
                  <div>
                    <strong>
                      {item.name}
                    </strong>

                    <span>
                      {item.email}
                    </span>
                  </div>

                  <span className="role-badge">
                    {item.role}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default UserManagement;