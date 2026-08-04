import { useEffect, useState } from "react";
import * as api from "../api";
import { formatBytes, formatDate } from "../utils";

export default function DashboardView() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getDashboard().then(setData).catch((err) => setError(err.message));
  }, []);

  return (
    <div className="view-container">
      <div className="view-header">
        <h1 className="view-title">Dashboard</h1>
        <p className="view-description">Overview of your knowledge base.</p>
      </div>

      {error && <p style={{ color: "var(--color-danger)" }}>{error}</p>}

      {data && (
        <>
          <div className="dashboard-stats">
            <div className="stat-card">
              <span className="stat-label">Documents</span>
              <span className="stat-value">{data.total_documents}</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Chunks / Embeddings</span>
              <span className="stat-value">{data.total_chunks}</span>
            </div>
            <div className="stat-card">
              <span className="stat-label">Storage Used</span>
              <span className="stat-value">{formatBytes(data.total_storage_bytes)}</span>
            </div>
          </div>

          <div className="card-panel">
            <div className="panel-header">
              <h3 className="panel-title">Recent Chats</h3>
            </div>
            <div className="table-container">
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>Question</th>
                    <th>Grounded</th>
                    <th>Time</th>
                  </tr>
                </thead>
                <tbody>
                  {data.recent_chats.map((chat) => (
                    <tr key={chat.id}>
                      <td>{chat.question}</td>
                      <td>{chat.grounded ? "Yes" : "No"}</td>
                      <td>{formatDate(chat.timestamp)}</td>
                    </tr>
                  ))}
                  {data.recent_chats.length === 0 && (
                    <tr>
                      <td colSpan={3} className="no-history-placeholder">
                        No chats yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
