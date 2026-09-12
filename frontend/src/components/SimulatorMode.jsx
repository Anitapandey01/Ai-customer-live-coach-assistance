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
            data.detail || "Unable to load simulator configuration."
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
      setError("Authentication token not found. Please login again.");
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
            expected_resolution: expectedResolution.trim(),
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
      return "";
    }

    return escalationRisk.risk_level.toLowerCase();
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

            <h1>Session Configuration</h1>

            <p>
              Loading customer simulator configuration...
            </p>
          </div>
        </div>
      </section>
    );
  }

  /*
   * SESSION CONFIGURATION
   *
   * This screen is intentionally separate from the
   * live conversation layout. The customer profile is
   * configured here before the simulation starts.
   */
  if (!sessionId) {
    return (
      <section className="simulator-setup-page">
        <div className="simulator-setup-container">
          <div className="simulator-setup-heading">
            <button
              type="button"
              className="back-button"
              onClick={onBack}
            >
              ← Back
            </button>

            <div className="simulator-setup-title">
              <span className="eyebrow">
                SESSION CONFIGURATION
              </span>

              <h1>Set up your customer</h1>

              <p>
                Configure the customer profile before
                starting the simulation.
              </p>
            </div>
          </div>

          {error && (
            <p className="login-error setup-error">
              {error}
            </p>
          )}

          <div className="simulator-setup-card">
            <div className="setup-section">
              <div className="setup-section-heading">
                <span className="setup-step">01</span>

                <div>
                  <h2>Customer Profile</h2>
                  <p>
                    Define who the simulated customer is.
                  </p>
                </div>
              </div>

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
                    disabled={isStarting}
                  >
                    {config?.personas?.map((item) => (
                      <option
                        key={item.id}
                        value={item.id}
                      >
                        {item.id.charAt(0).toUpperCase() +
                          item.id.slice(1)}
                      </option>
                    ))}
                  </select>

                  {getPersonaDescription() && (
                    <span className="setup-helper">
                      {getPersonaDescription()}
                    </span>
                  )}
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
                    disabled={isStarting}
                  >
                    {config?.emotions?.map((item) => (
                      <option
                        key={item}
                        value={item}
                      >
                        {item.charAt(0).toUpperCase() +
                          item.slice(1)}
                      </option>
                    ))}
                  </select>

                  <span className="setup-helper">
                    Determines the customer's initial
                    emotional state.
                  </span>
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
                    disabled={isStarting}
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

                  {getScenarioDescription() && (
                    <span className="setup-helper">
                      {getScenarioDescription()}
                    </span>
                  )}
                </div>
              </div>
            </div>

            <div className="setup-divider" />

            <div className="setup-section">
              <div className="setup-section-heading">
                <span className="setup-step">02</span>

                <div>
                  <h2>Interaction Conditions</h2>
                  <p>
                    Control the difficulty and customer
                    behavior during the simulation.
                  </p>
                </div>
              </div>

              <div className="setup-form">
                <div className="setup-field">
                  <div className="range-label-row">
                    <label htmlFor="issue-severity">
                      Issue Severity
                    </label>

                    <strong>
                      {issueSeverity}/5
                    </strong>
                  </div>

                  <input
                    id="issue-severity"
                    className="setup-range"
                    type="range"
                    min={config?.issue_severity?.min || 1}
                    max={config?.issue_severity?.max || 5}
                    value={issueSeverity}
                    onChange={(event) =>
                      setIssueSeverity(event.target.value)
                    }
                    disabled={isStarting}
                  />

                  <div className="range-scale">
                    <span>Low</span>
                    <span>High</span>
                  </div>
                </div>

                <div className="setup-field">
                  <div className="range-label-row">
                    <label htmlFor="patience-level">
                      Customer Patience
                    </label>

                    <strong>
                      {patienceLevel}%
                    </strong>
                  </div>

                  <input
                    id="patience-level"
                    className="setup-range"
                    type="range"
                    min={config?.patience_level?.min || 1}
                    max={config?.patience_level?.max || 100}
                    value={patienceLevel}
                    onChange={(event) =>
                      setPatienceLevel(event.target.value)
                    }
                    disabled={isStarting}
                  />

                  <div className="range-scale">
                    <span>Impatient</span>
                    <span>Patient</span>
                  </div>
                </div>

                <div className="setup-field">
                  <label htmlFor="expected-resolution">
                    Expected Resolution
                  </label>

                  <textarea
                    id="expected-resolution"
                    rows="4"
                    placeholder="What does the customer expect from the support agent?"
                    value={expectedResolution}
                    onChange={(event) =>
                      setExpectedResolution(event.target.value)
                    }
                    disabled={isStarting}
                  />

                  <span className="setup-helper">
                    Define the outcome the customer expects
                    from the interaction.
                  </span>
                </div>
              </div>
            </div>

            <div className="setup-footer">
              <div className="setup-footer-info">
                <span className="setup-footer-dot" />

                <span>
                  Your selections will remain fixed during
                  the simulation.
                </span>
              </div>

              <button
                type="button"
                className="primary-button setup-start-button"
                onClick={handleStartSimulation}
                disabled={
                  isStarting ||
                  !expectedResolution.trim()
                }
              >
                {isStarting
                  ? "Starting Simulation..."
                  : "Start Simulation →"}
              </button>
            </div>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="interaction-page">
      <div className="interaction-heading">
        <button
          type="button"
          className="back-button"
          onClick={handleBack}
        >
          ← Back
        </button>

        <div>
          <span className="eyebrow">
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
        <p className="login-error">
          {error}
        </p>
      )}

      <div className="interaction-layout">
        <aside className="settings-panel">
          <h3>Customer Profile</h3>

          <div className="active-session-badge">
            <span />
            Active
          </div>

          <div className="profile-detail">
            <span>Persona</span>
            <strong>
              {persona.charAt(0).toUpperCase() +
                persona.slice(1)}
            </strong>
          </div>

          <div className="profile-detail">
            <span>Scenario</span>
            <strong>
              {config?.scenarios?.find(
                (item) => item.id === scenario
              )?.title || "Customer Interaction"}
            </strong>
          </div>

          <div className="profile-detail">
            <span>Starting Emotion</span>
            <strong>
              {initialEmotion.charAt(0).toUpperCase() +
                initialEmotion.slice(1)}
            </strong>
          </div>

          <div className="profile-metrics">
            <div>
              <span>Issue Severity</span>
              <strong>{issueSeverity}/5</strong>
            </div>

            <div>
              <span>Patience</span>
              <strong>{patienceLevel}%</strong>
            </div>
          </div>

          <button
            type="button"
            className="secondary-button full-width"
            onClick={resetConversation}
            disabled={isSending}
          >
            Start New Simulation
          </button>
        </aside>

        <div className="conversation-panel">
          <div className="conversation-header">
            <div>
              <span>Live Simulation</span>

              <h3>
                {config?.scenarios?.find(
                  (item) => item.id === scenario
                )?.title || "Customer Interaction"}
              </h3>
            </div>

            <span className="status-dot">
              {isSending ? "Thinking..." : "Live"}
            </span>
          </div>

          <div className="simulator-state">
            <div>
              <span>Customer Emotion</span>
              <strong>
                {emotion.charAt(0).toUpperCase() +
                  emotion.slice(1)}
              </strong>
            </div>

            <div>
              <span>Emotion Score</span>
              <strong>
                {emotionScore}/100
              </strong>
            </div>

            <div>
              <span>Turn</span>
              <strong>
                {turnNumber}
              </strong>
            </div>

            <div>
              <span>Satisfaction</span>
              <strong>
                {satisfactionStatus.charAt(0).toUpperCase() +
                  satisfactionStatus.slice(1)}
              </strong>
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
          </div>

          <div className="message-input-area">
            <input
              type="text"
              placeholder="Your response..."
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
              className="primary-button"
              onClick={handleSendResponse}
              disabled={
                isSending ||
                !supportResponse.trim()
              }
            >
              {isSending ? "Sending..." : "Send"}
            </button>
          </div>

          <div className="analysis-panel">
            <div className="analysis-header">
              <div>
                <span className="eyebrow">
                  AI COACH
                </span>

                <h3>Conversation Analysis</h3>
              </div>

              {analysis?.confidence_score !== undefined && (
                <div className="confidence-score">
                  <span>Confidence</span>
                  <strong>
                    {analysis.confidence_score}%
                  </strong>
                </div>
              )}
            </div>

            {analysis && (
              <div className="analysis-grid">
                <div>
                  <span>Intent</span>
                  <strong>
                    {analysis.intent || "Unknown"}
                  </strong>
                </div>

                <div>
                  <span>Sentiment</span>
                  <strong>
                    {analysis.sentiment || "Neutral"}
                  </strong>
                </div>

                <div>
                  <span>Emotion</span>
                  <strong>
                    {analysis.emotion || "Calm"}
                  </strong>
                </div>

                <div>
                  <span>Frustration</span>
                  <strong>
                    {analysis.frustration_level ?? 0}/10
                  </strong>
                </div>
              </div>
            )}

            {escalationRisk && (
              <div
                className={`risk-panel ${getRiskClass()}`}
              >
                <div>
                  <span>Escalation Risk</span>
                  <strong>
                    {escalationRisk.risk_level}{" "}
                    {escalationRisk.risk_score}%
                  </strong>
                </div>

                {escalationRisk.reasons?.length > 0 && (
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
              <div className="coaching-panel">
                <span>Suggested Reply</span>

                <p>
                  {coaching.suggested_reply ||
                    "No suggested reply available."}
                </p>

                <span>Coach Tip</span>

                <p>
                  {coaching.coach_tip ||
                    "No coaching tip available."}
                </p>
              </div>
            )}

            {knowledge && (
              <div className="knowledge-panel">
                <div>
                  <span>Knowledge Recommendation</span>

                  <p>
                    {knowledge.answer ||
                      "No knowledge recommendation available."}
                  </p>
                </div>

                {knowledge.sources?.length > 0 && (
                  <div>
                    <span>Sources</span>

                    <ul>
                      {knowledge.sources.map(
                        (source, index) => (
                          <li
                            key={
                              source.chunk_id || index
                            }
                          >
                            {source.document_name}
                            {source.page_number
                              ? ` — Page ${source.page_number}`
                              : ""}
                          </li>
                        )
                      )}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

export default SimulatorMode;