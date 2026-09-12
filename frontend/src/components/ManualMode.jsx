import { useState } from "react";

function ManualMode({ onBack }) {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);

  const handleSend = () => {
    const trimmedMessage = message.trim();

    if (!trimmedMessage) {
      return;
    }

    setMessages((previousMessages) => [
      ...previousMessages,
      {
        id: Date.now(),
        sender: "customer",
        text: trimmedMessage,
      },
    ]);

    setMessage("");
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
          <span className="eyebrow">MANUAL MODE</span>
          <h1>Enter customer messages</h1>
          <p>
            Add incoming customer messages manually to start an interaction.
          </p>
        </div>
      </div>

      <div className="manual-panel">
        <div className="conversation-header">
          <div>
            <span>Conversation</span>
            <h3>Live Customer Interaction</h3>
          </div>

          <span className="status-dot">Ready</span>
        </div>

        <div className="messages-area manual-messages">
          {messages.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">✦</div>

              <h3>No messages yet</h3>

              <p>
                Enter a customer message below to begin.
              </p>
            </div>
          ) : (
            messages.map((item) => (
              <div
                key={item.id}
                className="message customer-message"
              >
                <span className="message-label">
                  Customer
                </span>

                <p>{item.text}</p>
              </div>
            ))
          )}
        </div>

        <div className="message-input-area">
          <input
            type="text"
            placeholder="Type customer message..."
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                handleSend();
              }
            }}
          />

          <button
            type="button"
            className="primary-button"
            onClick={handleSend}
          >
            Send
          </button>
        </div>
      </div>
    </section>
  );
}

export default ManualMode;