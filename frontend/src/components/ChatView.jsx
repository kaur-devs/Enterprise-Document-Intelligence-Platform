import { useEffect, useRef, useState } from "react";
import * as api from "../api";
import { SendIcon } from "../icons";

function historyToMessages(history) {
  const messages = [];
  for (const entry of [...history].reverse()) {
    messages.push({ role: "user", content: entry.question });
    messages.push({
      role: "bot",
      content: entry.answer,
      grounded: entry.grounded,
      citations: entry.sources,
    });
  }
  return messages;
}

export default function ChatView({ documents }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const scrollRef = useRef(null);

  useEffect(() => {
    api
      .getHistory()
      .then((history) => setMessages(historyToMessages(history)))
      .catch(() => {});
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  function toggleDocument(id) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const question = input.trim();
    if (!question || loading) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);
    try {
      const response = await api.askQuestion(question, [...selectedIds]);
      setMessages((prev) => [
        ...prev,
        { role: "bot", content: response.answer, grounded: response.grounded, citations: response.sources },
      ]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "bot", content: err.message, grounded: false, citations: [] }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="view-container">
      <div className="view-header">
        <h1 className="view-title">Chat</h1>
        <p className="view-description">Ask questions grounded in your uploaded documents.</p>
      </div>

      <div className="chat-view-container">
        <div className="chat-panel">
          <div className="chat-messages" ref={scrollRef}>
            {messages.map((msg, i) => (
              <div key={i} className={`message-bubble ${msg.role}`}>
                {msg.content}
                {msg.role === "bot" && msg.grounded === false && (
                  <div className="fallback-indicator">⚠ Not grounded in your documents</div>
                )}
                {msg.role === "bot" && msg.citations?.length > 0 && (
                  <div className="citations-list">
                    {msg.citations.map((c, j) => (
                      <span key={j} className="citation-chip">
                        {c.document_name} · p.{c.page}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {loading && <div className="message-bubble bot">Thinking…</div>}
          </div>
          <div className="chat-input-area">
            <form className="chat-form" onSubmit={handleSubmit}>
              <input
                className="chat-input"
                placeholder="Ask a question about your documents…"
                value={input}
                onChange={(e) => setInput(e.target.value)}
              />
              <button className="btn-primary" type="submit" disabled={loading || !input.trim()}>
                <SendIcon />
              </button>
            </form>
          </div>
        </div>

        <div className="scope-panel">
          <h3 className="scope-title">Search scope</h3>
          <div className="scope-list">
            <label className="scope-item">
              <input
                type="checkbox"
                className="scope-checkbox"
                checked={selectedIds.size === 0}
                onChange={() => setSelectedIds(new Set())}
              />
              All documents
            </label>
            {documents.map((doc) => (
              <label key={doc.id} className="scope-item">
                <input
                  type="checkbox"
                  className="scope-checkbox"
                  checked={selectedIds.has(doc.id)}
                  onChange={() => toggleDocument(doc.id)}
                />
                {doc.name}
              </label>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
