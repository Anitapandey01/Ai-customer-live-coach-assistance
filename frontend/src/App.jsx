import { useEffect, useState } from "react";
import Login from "./components/Login";
import Register from "./components/Register";
import ModeSelection from "./components/ModeSelection";
import SimulatorMode from "./components/SimulatorMode";
import ManualMode from "./components/ManualMode";
import ReplayMode from "./components/ReplayMode";
import Header from "./components/Header";
import UserManagement from "./components/UserManagement";
import KnowledgeBase from "./components/KnowledgeBase";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const [selectedMode, setSelectedMode] = useState(null);
  const [showRegister, setShowRegister] = useState(false);
  const [showUserManagement, setShowUserManagement] =
    useState(false);
  const [showKnowledgeBase, setShowKnowledgeBase] =
    useState(false);
  const [isInitializing, setIsInitializing] = useState(true);

  // =========================
  // Restore and Validate Session
  // =========================

  useEffect(() => {
    const restoreSession = async () => {
      const storedToken =
        localStorage.getItem("access_token");

      if (!storedToken) {
        setIsInitializing(false);
        return;
      }

      try {
        const response = await fetch(
          "http://127.0.0.1:8000/auth/me",
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${storedToken}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error(
            "Session is invalid or expired."
          );
        }

        const currentUser = await response.json();

        const restoredUser = {
          user_id: currentUser.user_id,
          name: currentUser.name,
          email: currentUser.email,
          role: currentUser.role,
          access_token: storedToken,
        };

        localStorage.setItem(
          "user",
          JSON.stringify({
            user_id: currentUser.user_id,
            name: currentUser.name,
            email: currentUser.email,
            role: currentUser.role,
          })
        );

        setUser(restoredUser);
        setIsLoggedIn(true);
      } catch (error) {
        console.error(
          "Unable to restore authenticated session:",
          error
        );

        localStorage.removeItem("access_token");
        localStorage.removeItem("user");

        setUser(null);
        setIsLoggedIn(false);
      } finally {
        setIsInitializing(false);
      }
    };

    restoreSession();
  }, []);

  // =========================
  // Login
  // =========================

  const handleLogin = (loginData) => {
    setUser(loginData);
    setIsLoggedIn(true);
    setShowRegister(false);
    setSelectedMode(null);
    setShowUserManagement(false);
    setShowKnowledgeBase(false);
  };

  // =========================
  // Logout
  // =========================

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    setIsLoggedIn(false);
    setUser(null);
    setSelectedMode(null);
    setShowRegister(false);
    setShowUserManagement(false);
    setShowKnowledgeBase(false);
  };

  // =========================
  // Mode Selection
  // =========================

  const handleModeSelect = (mode) => {
    setSelectedMode(mode);
    setShowUserManagement(false);
    setShowKnowledgeBase(false);
  };

  const handleBackToModes = () => {
    setSelectedMode(null);
    setShowUserManagement(false);
    setShowKnowledgeBase(false);
  };

  // =========================
  // Registration
  // =========================

  const handleRegisterSuccess = () => {
    setShowRegister(false);
  };

  // =========================
  // Session Loading
  // =========================

  if (isInitializing) {
    return (
      <div className="login-page">
        <div className="login-card">
          <div className="brand-section">
            <div className="brand-icon">AI</div>

            <h1>SupportAI</h1>

            <p>
              Verifying your session...
            </p>
          </div>
        </div>
      </div>
    );
  }

  // =========================
  // Authentication Screens
  // =========================

  if (!isLoggedIn) {
    if (showRegister) {
      return (
        <Register
          onRegisterSuccess={handleRegisterSuccess}
          onBackToLogin={() =>
            setShowRegister(false)
          }
        />
      );
    }

    return (
      <Login
        onLogin={handleLogin}
        onRegister={() =>
          setShowRegister(true)
        }
      />
    );
  }

  // =========================
  // Role Permissions
  // =========================

  const isAdmin = user?.role === "admin";
  const isEmployee = user?.role === "employee";
  const isCustomer = user?.role === "customer";

  const canAccessKnowledgeBase =
    isAdmin || isEmployee;

  // =========================
  // Admin: User Management
  // =========================

  if (showUserManagement) {
    if (!isAdmin) {
      setShowUserManagement(false);
      return null;
    }

    return (
      <div className="app">
        <Header
          user={user}
          onLogout={handleLogout}
        />

        <main className="main-content">
          <UserManagement
            user={user}
            onBack={() =>
              setShowUserManagement(false)
            }
          />
        </main>
      </div>
    );
  }

  // =========================
  // Admin / Employee:
  // Knowledge Base
  // =========================

  if (showKnowledgeBase) {
    if (!canAccessKnowledgeBase) {
      setShowKnowledgeBase(false);
      return null;
    }

    return (
      <div className="app">
        <Header
          user={user}
          onLogout={handleLogout}
        />

        <main className="main-content">
          <KnowledgeBase
            user={user}
            onBack={() =>
              setShowKnowledgeBase(false)
            }
          />
        </main>
      </div>
    );
  }

  // =========================
  // Main Application
  // =========================

  return (
    <div className="app">
      <Header
        user={user}
        onLogout={handleLogout}
      />

      <main className="main-content">

        {/* =========================
            ADMIN / EMPLOYEE CONTROLS
            ========================= */}

        {(isAdmin || isEmployee) && (
          <div className="admin-actions">

            {/* Admin only */}
            {isAdmin && (
              <button
                type="button"
                className="secondary-button"
                onClick={() => {
                  setShowUserManagement(true);
                  setShowKnowledgeBase(false);
                  setSelectedMode(null);
                }}
              >
                User Management
              </button>
            )}

            {/* Admin + Employee */}
            <button
              type="button"
              className="secondary-button"
              onClick={() => {
                setShowKnowledgeBase(true);
                setShowUserManagement(false);
                setSelectedMode(null);
              }}
            >
              Knowledge Base
            </button>
          </div>
        )}

        {/* =========================
            CUSTOMER / EMPLOYEE / ADMIN
            SUPPORT MODES
            ========================= */}

        {!selectedMode && (
          <ModeSelection
            user={user}
            onSelectMode={handleModeSelect}
          />
        )}

        {selectedMode === "simulator" && (
          <SimulatorMode
            onBack={handleBackToModes}
          />
        )}

        {selectedMode === "manual" && (
          <ManualMode
            onBack={handleBackToModes}
          />
        )}

        {selectedMode === "replay" && (
          <ReplayMode
            onBack={handleBackToModes}
          />
        )}
      </main>
    </div>
  );
}

export default App;