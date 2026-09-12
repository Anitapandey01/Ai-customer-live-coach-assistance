import { useState } from "react";

function ReplayMode({ onBack }) {
  const transcripts = [
    {
      id: "refund",
      title: "Refund Request",
      messages: [
        "I want to request a refund for my recent purchase.",
        "I have already used the product. Am I still eligible?",
        "What information do I need to provide?",
      ],
    },
    {
      id: "delivery",
      title: "Delayed Delivery",
      messages: [
        "My order has not arrived yet.",
        "It has already been several days.",
        "Can you please check the status of my order?",
      ],
    },
  ];

  const [selectedTranscript, setSelectedTranscript] =
    useState(transcripts[0].id);

  const [currentMessage, setCurrentMessage] = useState(0);

  const transcript = transcripts.find(
    (item) => item.id === selectedTranscript
  );

  const handleTranscriptChange = (event) => {
    setSelectedTranscript(event.target.value);
    setCurrentMessage(0);
  };

  const handlePrevious = () => {
    setCurrentMessage((previous) =>
      Math.max(previous - 1, 0)
    );
  };

  const handleNext = () => {
    setCurrentMessage((previous) =>
      Math.min(
        previous + 1,
        transcript.messages.length - 1
      )
    );
  };

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
          <span className="eyebrow">REPLAY MODE</span>
          <h1>Replay a support interaction</h1>
          <p>
            Review a pre-loaded conversation one message at a time.
          </p>
        </div>
      </div>

      <div className="replay-layout">
        <aside className="settings-panel">
          <h3>Transcript</h3>

          <label htmlFor="transcript">
            Select conversation
          </label>

          <select
            id="transcript"
            value={selectedTranscript}
            onChange={handleTranscriptChange}
          >
            {transcripts.map((item) => (
              <option key={item.id} value={item.id}>
                {item.title}
              </option>
            ))}
          </select>

          <div className="replay-progress">
            <span>
              Message {currentMessage + 1} of{" "}
              {transcript.messages.length}
            </span>

            <div className="progress-track">
              <div
                className="progress-value"
                style={{
                  width: `${
                    ((currentMessage + 1) /
                      transcript.messages.length) *
                    100
                  }%`,
                }}
              />
            </div>
          </div>
        </aside>

        <div className="replay-conversation">
          <div className="conversation-header">
            <div>
              <span>Replay</span>
              <h3>{transcript.title}</h3>
            </div>

            <span className="status-dot">Replay</span>
          </div>

          <div className="replay-message">
            <span className="message-label">
              Customer
            </span>

            <p>{transcript.messages[currentMessage]}</p>
          </div>

          <div className="replay-controls">
            <button
              type="button"
              className="secondary-button"
              onClick={handlePrevious}
              disabled={currentMessage === 0}
            >
              ← Previous
            </button>

            <span>
              {currentMessage + 1} /{" "}
              {transcript.messages.length}
            </span>

            <button
              type="button"
              className="primary-button"
              onClick={handleNext}
              disabled={
                currentMessage ===
                transcript.messages.length - 1
              }
            >
              Next →
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

export default ReplayMode;