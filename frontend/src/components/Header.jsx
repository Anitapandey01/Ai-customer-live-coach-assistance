function Header({ user, onLogout }) {
  return (
    <header className="header">
      <div className="header-brand">
        <div className="small-brand-icon">AI</div>

        <div>
          <h2>SupportAI</h2>
          <span>Customer Support Assistant</span>
        </div>
      </div>

      <div className="header-actions">
        <div className="user-info">
          <span className="user-name">
            {user?.email}
          </span>

          <span className="role-badge">
            {user?.role}
          </span>
        </div>

        <button
          type="button"
          className="logout-button"
          onClick={onLogout}
        >
          Logout
        </button>
      </div>
    </header>
  );
}

export default Header;