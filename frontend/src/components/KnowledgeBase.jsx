import { useRef, useState } from "react";
import * as api from "../api";
import { formatBytes, formatDate } from "../utils";
import { UploadIcon, TrashIcon, RefreshIcon } from "../icons";

function Modal({ title, icon, tone, children, onClose, actions }) {
  return (
    <div className="custom-modal-overlay" onClick={onClose}>
      <div className="custom-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span className={`modal-icon ${tone}`}>{icon}</span>
          <h3 className="modal-title">{title}</h3>
        </div>
        <div className="modal-body">{children}</div>
        <div className="modal-actions">{actions}</div>
      </div>
    </div>
  );
}

export default function KnowledgeBase({ documents, onRefresh }) {
  const fileInputRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [pendingDuplicate, setPendingDuplicate] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [reindexingId, setReindexingId] = useState(null);

  async function handleUpload(file, override) {
    setUploading(true);
    setError("");
    try {
      const result = await api.uploadDocument(file, override);
      if (result.status === "likely_duplicate") {
        setPendingDuplicate({ file, message: result.message });
        return;
      }
      setPendingDuplicate(null);
      await onRefresh();
    } catch (err) {
      if (err.status === 409) {
        setError(err.data?.message || "This document already exists.");
      } else {
        setError(err.message);
      }
    } finally {
      setUploading(false);
    }
  }

  function handleFileChange(e) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (file) handleUpload(file, false);
  }

  async function handleReindex(doc) {
    setReindexingId(doc.id);
    try {
      await api.reindexDocument(doc.id);
      await onRefresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setReindexingId(null);
    }
  }

  async function confirmDelete() {
    const target = deleteTarget;
    setDeleteTarget(null);
    try {
      await api.deleteDocument(target.id);
      await onRefresh();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="view-container">
      <div className="view-header">
        <h1 className="view-title">Knowledge Base</h1>
        <p className="view-description">Upload documents to make them searchable and chat-ready.</p>
      </div>

      <div className="card-panel" style={{ marginBottom: 32 }}>
        <div
          className="upload-zone"
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            const file = e.dataTransfer.files?.[0];
            if (file) handleUpload(file, false);
          }}
        >
          <UploadIcon className="upload-icon" width={28} height={28} />
          <p className="upload-text">
            {uploading ? "Uploading…" : "Click or drag a PDF, DOCX, TXT, or Markdown file here"}
          </p>
          <input
            ref={fileInputRef}
            type="file"
            className="file-input"
            accept=".pdf,.docx,.doc,.txt,.md,.markdown"
            onChange={handleFileChange}
          />
        </div>
        {error && <p style={{ color: "var(--color-danger)", marginTop: 12 }}>{error}</p>}
      </div>

      <div className="card-panel">
        <div className="panel-header">
          <h3 className="panel-title">Documents ({documents.length})</h3>
        </div>
        <div className="table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Size</th>
                <th>Chunks</th>
                <th>Status</th>
                <th>Uploaded</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.id}>
                  <td>{doc.name}</td>
                  <td>{doc.type}</td>
                  <td>{formatBytes(doc.size)}</td>
                  <td>{doc.chunk_count}</td>
                  <td>
                    <span className={`status-badge ${doc.status}`}>{doc.status}</span>
                  </td>
                  <td>{formatDate(doc.upload_time)}</td>
                  <td>
                    <button
                      className="btn-icon"
                      disabled={reindexingId === doc.id}
                      onClick={() => handleReindex(doc)}
                      title="Re-index"
                    >
                      <RefreshIcon />
                    </button>
                    <button className="btn-icon" onClick={() => setDeleteTarget(doc)} title="Delete">
                      <TrashIcon />
                    </button>
                  </td>
                </tr>
              ))}
              {documents.length === 0 && (
                <tr>
                  <td colSpan={7} className="no-history-placeholder">
                    No documents uploaded yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {pendingDuplicate && (
        <Modal
          title="Possible duplicate"
          icon="⚠"
          tone="warning"
          onClose={() => setPendingDuplicate(null)}
          actions={
            <>
              <button className="btn-secondary" onClick={() => setPendingDuplicate(null)}>
                Cancel
              </button>
              <button
                className="btn-primary"
                onClick={() => handleUpload(pendingDuplicate.file, true)}
              >
                Upload anyway
              </button>
            </>
          }
        >
          {pendingDuplicate.message}
        </Modal>
      )}

      {deleteTarget && (
        <Modal
          title="Delete document"
          icon="✕"
          tone="danger"
          onClose={() => setDeleteTarget(null)}
          actions={
            <>
              <button className="btn-secondary" onClick={() => setDeleteTarget(null)}>
                Cancel
              </button>
              <button className="btn-danger" onClick={confirmDelete}>
                Delete
              </button>
            </>
          }
        >
          Delete "{deleteTarget.name}" and all its indexed content? This can't be undone.
        </Modal>
      )}
    </div>
  );
}
