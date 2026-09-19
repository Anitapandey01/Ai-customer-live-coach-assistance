import { useEffect, useState } from "react";

function SimulatorMode({ onBack }) {
  const [config, setConfig] = useState(null);

  const [persona, setPersona] = useState("calm");
  const [initialEmotion, setInitialEmotion] = useState("calm");
  const [scenario, setScenario] = useState("refund");
  const [issueSeverity, setIssueSeverity] = useState(3);
  const [patienceLevel, setPatienceLevel] = useState(60);
  const [expectedResolution, setExpectedResolution] = useState(
    "A fair resolution to the issue."
  );

  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);

  const [emotion, setEmotion] = useState("calm");
  const [emotionScore, setEmotionScore] = useState(15);
  const [turnNumber, setTurnNumber] = useState(0);
  const [satisfactionStatus, setSatisfactionStatus] =
    useState("unsatisfied");

  const [analysis, setAnalysis] = useState(null);
  const [knowledge, setKnowledge] = useState(null);
  const [coaching, setCoaching] = useState(null);
  const [escalationRisk, setEscalationRisk] = useState(null);

  const [activeCoachTab, setActiveCoachTab] =
    useState("suggestions");

  const [isLoadingConfig, setIsLoadingConfig] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [isSending, setIsSending] = useState(false);

  const [supportResponse, setSupportResponse] = useState("");
  const [error, setError] = useState("");

  const token = localStorage.getItem("access_token");

  useEffect(() => {
    const fetchConfig = async () => {
      setIsLoadingConfig(true);
      setError("");

      try {
        const response = await fetch(
          "http://127.0.0.1:8000/simulator/config",
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.detail ||
              "Unable to load simulator configuration."
          );
        }

        setConfig(data);

        if (data.personas?.length > 0) {
          setPersona(data.personas[0].id);
        }

        if (data.emotions?.length > 0) {
          setInitialEmotion(data.emotions[0]);
        }

        if (data.scenarios?.length > 0) {
          setScenario(data.scenarios[0].id);
        }
      } catch (error) {
        setError(
          error.message ||
            "Unable to load simulator configuration."
        );
      } finally {
        setIsLoadingConfig(false);
      }
    };

    if (token) {
      fetchConfig();
    } else {
      setError(
        "Authentication token not found. Please login again."
      );
      setIsLoadingConfig(false);
    }
  }, [token]);

  const resetConversation = () => {
    setSessionId(null);
    setMessages([]);

    setEmotion(initialEmotion);
    setEmotionScore(15);
    setTurnNumber(0);
    setSatisfactionStatus("unsatisfied");

    setAnalysis(null);
    setKnowledge(null);
    setCoaching(null);
    setEscalationRisk(null);

    setActiveCoachTab("suggestions");

    setSupportResponse("");
  };

  const updateBackendResults = (data) => {
    setEmotion(data.state?.emotion || "calm");
    setEmotionScore(data.state?.emotion_score ?? 15);
    setTurnNumber(data.state?.turn_number ?? 0);

    setSatisfactionStatus(
      data.state?.satisfaction_status || "unsatisfied"
    );

    setAnalysis(data.analysis || null);
    setKnowledge(data.knowledge || null);
    setCoaching(data.coaching || null);
    setEscalationRisk(data.escalation_risk || null);
  };

  const handleStartSimulation = async () => {
    setError("");
    setIsStarting(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/simulator/start",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            persona,
            initial_emotion: initialEmotion,
            scenario,
            issue_severity: Number(issueSeverity),
            patience_level: Number(patienceLevel),
            expected_resolution:
              expectedResolution.trim(),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to start simulation."
        );
      }

      setSessionId(data.session_id);

      setMessages([
        {
          id: `${data.session_id}-1`,
          sender: "customer",
          text: data.customer_message,
        },
      ]);

      updateBackendResults(data);
      setSupportResponse("");
      setActiveCoachTab("suggestions");
    } catch (error) {
      setError(
        error.message ||
          "Unable to start the customer simulation."
      );
    } finally {
      setIsStarting(false);
    }
  };

  const handleSendResponse = async () => {
    const trimmedResponse = supportResponse.trim();

    if (!trimmedResponse || !sessionId) {
      return;
    }

    setError("");
    setIsSending(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/simulator/turn",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            session_id: sessionId,
            support_response: trimmedResponse,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Unable to generate the customer's response."
        );
      }

      const messageTimestamp = Date.now();

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          id: `${data.session_id}-${messageTimestamp}`,
          sender: "support_agent",
          text: trimmedResponse,
        },
        {
          id: `${data.session_id}-${messageTimestamp}-customer`,
          sender: "customer",
          text: data.customer_message,
        },
      ]);

      updateBackendResults(data);
      setSupportResponse("");
    } catch (error) {
      setError(
        error.message ||
          "Unable to generate the customer's response."
      );
    } finally {
      setIsSending(false);
    }
  };

  const handleUseSuggestedReply = () => {
    if (coaching?.suggested_reply) {
      setSupportResponse(coaching.suggested_reply);
    }
  };

  const handleBack = () => {
    resetConversation();
    onBack();
  };

  const getPersonaDescription = () => {
    if (!config?.personas) {
      return "";
    }

    const selectedPersona = config.personas.find(
      (item) => item.id === persona
    );

    return selectedPersona?.description || "";
  };

  const getScenarioDescription = () => {
    if (!config?.scenarios) {
      return "";
    }

    const selectedScenario = config.scenarios.find(
      (item) => item.id === scenario
    );

    return selectedScenario?.description || "";
  };

  const getRiskClass = () => {
    if (!escalationRisk?.risk_level) {
      return "low";
    }

    return escalationRisk.risk_level.toLowerCase();
  };

  const formatLabel = (value) => {
    if (!value) {
      return "Unknown";
    }

    return value.charAt(0).toUpperCase() + value.slice(1);
  };

  if (isLoadingConfig) {
    return (
      <section className="interaction-page">
        <div className="interaction-heading">
          <button
            type="button"
            className="back-button"
            onClick={onBack}
          >
            ← Back
          </button>

          <div>
            <span className="eyebrow">
              SIMULATOR MODE
            </span>

            <h1>Practice a customer interaction</h1>

            <p>
              Loading customer simulator configuration...
            </p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="interaction-page simulator-page">
      <div className="interaction-heading simulator-heading">
        <button
          type="button"
          className="back-button"
          onClick={handleBack}
        >
          ← Back
        </button>

        <div>
          <span className="eyebrow simulator-eyebrow">
            SIMULATOR MODE
          </span>

          <h1>Practice a customer interaction</h1>

          <p>
            The AI simulates a customer based on the
            selected persona, scenario, and emotional state.
          </p>
        </div>
      </div>

      {error && (
        <div className="simulator-error">
          {error}
        </div>
      )}

      {!sessionId ? (
        <div className="simulation-setup">
          <aside className="settings-panel setup-profile-panel">
            <div className="profile-header">
              <div>
                <span className="panel-eyebrow">
                  CUSTOMER PROFILE
                </span>

                <h2>Set up your customer</h2>
              </div>

              <span className="ready-badge">
                Ready
              </span>
            </div>

            <p className="setup-description">
              Configure the customer profile before
              starting the simulation.
            </p>

            <div className="setup-form">
              <div className="setup-field">
                <label htmlFor="persona">
                  Customer Persona
                </label>

                <select
                  id="persona"
                  value={persona}
                  onChange={(event) =>
                    setPersona(event.target.value)
                  }
                >
                  {config?.personas?.map((item) => (
                    <option
                      key={item.id}
                      value={item.id}
                    >
                      {formatLabel(item.id)}
                    </option>
                  ))}
                </select>

                <p className="field-description">
                  {getPersonaDescription()}
                </p>
              </div>

              <div className="setup-field">
                <label htmlFor="initial-emotion">
                  Starting Emotion
                </label>

                <select
                  id="initial-emotion"
                  value={initialEmotion}
                  onChange={(event) =>
                    setInitialEmotion(event.target.value)
                  }
                >
                  {config?.emotions?.map((item) => (
                    <option
                      key={item}
                      value={item}
                    >
                      {formatLabel(item)}
                    </option>
                  ))}
                </select>

                <p className="field-description">
                  Determines the customer's initial
                  emotional state.
                </p>
              </div>

              <div className="setup-field">
                <label htmlFor="scenario">
                  Customer Scenario
                </label>

                <select
                  id="scenario"
                  value={scenario}
                  onChange={(event) =>
                    setScenario(event.target.value)
                  }
                >
                  {config?.scenarios?.map((item) => (
                    <option
                      key={item.id}
                      value={item.id}
                    >
                      {item.title}
                    </option>
                  ))}
                </select>

                <p className="field-description">
                  {getScenarioDescription()}
                </p>
              </div>

              <div className="setup-two-column">
                <div className="setup-field">
                  <div className="field-label-row">
                    <label htmlFor="issue-severity">
                      Issue Severity
                    </label>

                    <span>
                      {issueSeverity}/5
                    </span>
                  </div>

                  <input
                    id="issue-severity"
                    className="range-input"
                    type="range"
                    min={config?.issue_severity?.min || 1}
                    max={config?.issue_severity?.max || 5}
                    value={issueSeverity}
                    onChange={(event) =>
                      setIssueSeverity(
                        Number(event.target.value)
                      )
                    }
                  />

                  <div className="range-labels">
                    <span>Low</span>
                    <span>High</span>
                  </div>
                </div>

                <div className="setup-field">
                  <div className="field-label-row">
                    <label htmlFor="patience-level">
                      Customer Patience
                    </label>

                    <span>
                      {patienceLevel}%
                    </span>
                  </div>

                  <input
                    id="patience-level"
                    className="range-input patience-range"
                    type="range"
                    min={
                      config?.patience_level?.min || 1
                    }
                    max={
                      config?.patience_level?.max || 100
                    }
                    value={patienceLevel}
                    onChange={(event) =>
                      setPatienceLevel(
                        Number(event.target.value)
                      )
                    }
                  />

                  <div className="range-labels">
                    <span>Impatient</span>
                    <span>Patient</span>
                  </div>
                </div>
              </div>

              <div className="setup-field">
                <label htmlFor="expected-resolution">
                  Expected Resolution
                </label>

                <textarea
                  id="expected-resolution"
                  rows="4"
                  placeholder="What does the customer expect?"
                  value={expectedResolution}
                  onChange={(event) =>
                    setExpectedResolution(
                      event.target.value
                    )
                  }
                />
              </div>

              <button
                type="button"
                className="primary-button start-button"
                onClick={handleStartSimulation}
                disabled={
                  isStarting ||
                  !expectedResolution.trim()
                }
              >
                {isStarting
                  ? "Starting Simulation..."
                  : "Start Simulation"}
              </button>
            </div>
          </aside>

          <div className="setup-preview">
            <div className="setup-preview-inner">
              <span className="preview-icon">
                ◈
              </span>

              <span className="panel-eyebrow">
                SIMULATOR PREVIEW
              </span>

              <h2>
                Practice realistic customer
                conversations
              </h2>

              <p>
                The customer will respond dynamically
                based on their persona, emotional state,
                patience, and the support response you
                provide.
              </p>

              <div className="preview-features">
                <div>
                  <strong>AI Customer</strong>
                  <span>
                    Dynamic multi-turn responses
                  </span>
                </div>

                <div>
                  <strong>Live Analysis</strong>
                  <span>
                    Intent, sentiment and emotion
                  </span>
                </div>

                <div>
                  <strong>AI Coaching</strong>
                  <span>
                    Guidance while you respond
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="simulation-workspace">
          <aside className="settings-panel customer-profile-panel">
            <div className="profile-header">
              <div>
                <span className="panel-eyebrow">
                  ACTIVE SESSION
                </span>

                <h2>Customer Profile</h2>
              </div>

              <span className="active-badge">
                <span />
                Active
              </span>
            </div>

            <div className="profile-details">
              <div className="profile-item">
                <span>Persona</span>
                <strong>
                  {formatLabel(persona)}
                </strong>
              </div>

              <div className="profile-item">
                <span>Scenario</span>
                <strong>
                  {config?.scenarios?.find(
                    (item) => item.id === scenario
                  )?.title || formatLabel(scenario)}
                </strong>
              </div>

              <div className="profile-item">
                <span>Starting Emotion</span>
                <strong>
                  {formatLabel(initialEmotion)}
                </strong>
              </div>

              <div className="profile-two-column">
                <div className="profile-item compact">
                  <span>Issue Severity</span>
                  <strong>
                    {issueSeverity}/5
                  </strong>
                </div>

                <div className="profile-item compact">
                  <span>Patience</span>
                  <strong>
                    {patienceLevel}%
                  </strong>
                </div>
              </div>
            </div>

            <button
              type="button"
              className="secondary-button full-width new-session-button"
              onClick={resetConversation}
              disabled={isSending}
            >
              Start New Simulation
            </button>
          </aside>

          <main className="conversation-panel">
            <div className="simulation-overview">
              <div className="conversation-header">
                <div>
                  <span className="live-label">
                    LIVE SIMULATION
                  </span>

                  <h2>
                    {config?.scenarios?.find(
                      (item) => item.id === scenario
                    )?.title ||
                      "Customer Interaction"}
                  </h2>
                </div>

                <span className="live-status">
                  <span />
                  Live
                </span>
              </div>

              <div className="customer-state-header">
                <div>
                  <span className="state-eyebrow">
                    CUSTOMER STATE
                  </span>

                  <p>
                    Live customer profile
                  </p>
                </div>

                <span className="turn-badge">
                  Turn {turnNumber}
                </span>
              </div>

              <div className="customer-state-grid">
                <div className="state-card">
                  <span>Emotion</span>
                  <strong>
                    {formatLabel(emotion)}
                  </strong>
                </div>

                <div className="state-card">
                  <span>Emotion Score</span>
                  <strong>
                    {emotionScore}
                    <small>/100</small>
                  </strong>
                </div>

                <div className="state-card">
                  <span>Satisfaction</span>
                  <strong>
                    {formatLabel(
                      satisfactionStatus
                    )}
                  </strong>
                </div>

                <div className="state-card">
                  <span>Issue Severity</span>
                  <strong>
                    {issueSeverity}
                    <small>/5</small>
                  </strong>
                </div>
              </div>
            </div>

            <div className="messages-area">
              {messages.map((item) => (
                <div
                  key={item.id}
                  className={`message ${
                    item.sender === "customer"
                      ? "customer-message"
                      : "support-message"
                  }`}
                >
                  <span className="message-label">
                    {item.sender === "customer"
                      ? "Customer"
                      : "You"}
                  </span>

                  <p>{item.text}</p>
                </div>
              ))}

              {isSending && (
                <div className="typing-indicator">
                  <span />
                  <span />
                  <span />
                  Customer is responding...
                </div>
              )}
            </div>

            <div className="message-input-area">
              <input
                type="text"
                placeholder="Type your response..."
                value={supportResponse}
                onChange={(event) =>
                  setSupportResponse(event.target.value)
                }
                onKeyDown={(event) => {
                  if (
                    event.key === "Enter" &&
                    !event.shiftKey
                  ) {
                    event.preventDefault();
                    handleSendResponse();
                  }
                }}
                disabled={isSending}
              />

              <button
                type="button"
                className="primary-button send-button"
                onClick={handleSendResponse}
                disabled={
                  isSending ||
                  !supportResponse.trim()
                }
              >
                {isSending ? "Sending..." : "Send"}
              </button>
            </div>
          </main>

          <aside className="ai-coach-panel">
            <div className="coach-header">
              <div>
                <span className="coach-icon">
                  ✦
                </span>

                <div>
                  <span className="panel-eyebrow">
                    AI COACH
                  </span>

                  <h2>Real-time guidance</h2>
                </div>
              </div>
            </div>

            <div className="coach-tabs">
              <button
                type="button"
                className={
                  activeCoachTab === "suggestions"
                    ? "active"
                    : ""
                }
                onClick={() =>
                  setActiveCoachTab("suggestions")
                }
              >
                Suggestions
              </button>

              <button
                type="button"
                className={
                  activeCoachTab === "knowledge"
                    ? "active"
                    : ""
                }
                onClick={() =>
                  setActiveCoachTab("knowledge")
                }
              >
                Knowledge
              </button>
            </div>

            {activeCoachTab === "suggestions" ? (
              <div className="coach-content">
                <div className="coach-analysis-card">
                  <div className="coach-analysis-header">
                    <div>
                      <span className="panel-eyebrow">
                        CONVERSATION ANALYSIS
                      </span>

                      <h3>
                        Current assessment
                      </h3>
                    </div>

                    {analysis?.confidence_score !==
                      undefined && (
                      <div className="confidence-mini">
                        <span>Confidence</span>
                        <strong>
                          {analysis.confidence_score}%
                        </strong>
                      </div>
                    )}
                  </div>

                  <div className="coach-metrics">
                    <div>
                      <span>Intent</span>
                      <strong>
                        {analysis?.intent ||
                          "Unknown"}
                      </strong>
                    </div>

                    <div>
                      <span>Sentiment</span>
                      <strong>
                        {analysis?.sentiment ||
                          "Neutral"}
                      </strong>
                    </div>

                    <div>
                      <span>Emotion</span>
                      <strong>
                        {analysis?.emotion ||
                          "Calm"}
                      </strong>
                    </div>

                    <div>
                      <span>Frustration</span>
                      <strong>
                        {analysis?.frustration_level ??
                          0}
                        /10
                      </strong>
                    </div>
                  </div>
                </div>

                {escalationRisk && (
                  <div
                    className={`escalation-card ${getRiskClass()}`}
                  >
                    <div className="escalation-top">
                      <div>
                        <span>
                          ESCALATION RISK
                        </span>

                        <strong>
                          {escalationRisk.risk_level}
                        </strong>
                      </div>

                      <strong className="risk-score">
                        {escalationRisk.risk_score}%
                      </strong>
                    </div>

                    {escalationRisk.reasons
                      ?.length > 0 && (
                      <ul>
                        {escalationRisk.reasons.map(
                          (reason, index) => (
                            <li key={index}>
                              {reason}
                            </li>
                          )
                        )}
                      </ul>
                    )}
                  </div>
                )}

                {coaching && (
                  <>
                    <div className="suggestion-card">
                      <div className="suggestion-card-header">
                        <span className="suggestion-icon">
                          ▣
                        </span>

                        <span>
                          SUGGESTED REPLY
                        </span>
                      </div>

                      <p>
                        {coaching.suggested_reply ||
                          "No suggested reply available."}
                      </p>

                      <button
                        type="button"
                        className="use-reply-button"
                        onClick={
                          handleUseSuggestedReply
                        }
                      >
                        Use This Reply
                      </button>
                    </div>

                    <div className="tip-card">
                      <div className="tip-card-header">
                        <span>♧</span>

                        <span>
                          COACH TIP
                        </span>
                      </div>

                      <p>
                        {coaching.coach_tip ||
                          "No coaching tip available."}
                      </p>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="coach-content knowledge-content">
                {knowledge ? (
                  <>
                    <div className="knowledge-card">
                      <div className="knowledge-card-header">
                        <span className="knowledge-icon">
                          ▤
                        </span>

                        <div>
                          <span className="panel-eyebrow">
                            KNOWLEDGE RECOMMENDATION
                          </span>

                          <h3>
                            Relevant information
                          </h3>
                        </div>
                      </div>

                      <p>
                        {knowledge.answer ||
                          "No knowledge recommendation available."}
                      </p>
                    </div>

                    {knowledge.sources?.length >
                      0 && (
                      <div className="sources-card">
                        <div className="sources-header">
                          <span className="panel-eyebrow">
                            SOURCES
                          </span>

                          <span>
                            {knowledge.sources.length}
                          </span>
                        </div>

                        <div className="sources-list">
                          {knowledge.sources.map(
                            (source, index) => (
                              <div
                                className="source-item"
                                key={
                                  source.chunk_id ||
                                  index
                                }
                              >
                                <div>
                                  <span className="source-icon">
                                    ◫
                                  </span>

                                  <div>
                                    <strong>
                                      {
                                        source.document_name
                                      }
                                    </strong>

                                    <span>
                                      {source.page_number
                                        ? `Page ${source.page_number}`
                                        : "Knowledge source"}
                                    </span>
                                  </div>
                                </div>

                                <span className="source-arrow">
                                  →
                                </span>
                              </div>
                            )
                          )}
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="coach-empty">
                    <span>▤</span>

                    <h3>
                      Knowledge unavailable
                    </h3>

                    <p>
                      Knowledge recommendations will
                      appear here after the simulation
                      starts.
                    </p>
                  </div>
                )}
              </div>
            )}
          </aside>
        </div>
      )}
    </section>
  );
}

export default SimulatorMode;