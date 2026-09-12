function ModeSelection({ onSelectMode }) {
  const modes = [
    {
      id: "simulator",
      number: "01",
      title: "Simulator Mode",
      description:
        "Practice customer interactions with an AI-generated customer based on a selected scenario.",
      icon: "◈",
    },
    {
      id: "manual",
      number: "02",
      title: "Manual Mode",
      description:
        "Enter customer messages manually and interact with the support assistant.",
      icon: "✦",
    },
    {
      id: "replay",
      number: "03",
      title: "Replay Mode",
      description:
        "Replay a pre-loaded customer support conversation message by message.",
      icon: "▶",
    },
  ];

  return (
    <section className="mode-page">
      <div className="page-heading">
        <span className="eyebrow">CUSTOMER SUPPORT</span>

        <h1>
          Choose your
          <span> interaction mode</span>
        </h1>

        <p>
          Select how you want to interact with the AI-powered
          customer support assistant.
        </p>
      </div>

      <div className="mode-grid">
        {modes.map((mode) => (
          <button
            type="button"
            key={mode.id}
            className="mode-card"
            onClick={() => onSelectMode(mode.id)}
          >
            <div className="mode-top">
              <span className="mode-number">
                {mode.number}
              </span>

              <span className="mode-icon">
                {mode.icon}
              </span>
            </div>

            <div className="mode-content">
              <h2>{mode.title}</h2>

              <p>{mode.description}</p>
            </div>

            <div className="mode-footer">
              <span>Start mode</span>
              <span className="arrow">→</span>
            </div>
          </button>
        ))}
      </div>
    </section>
  );
}

export default ModeSelection;