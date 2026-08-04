import { useState } from "react";
import * as api from "../api";
import { SearchIcon } from "../icons";

export default function SearchView({ documents }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [searched, setSearched] = useState(false);

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
    if (!query.trim() || loading) return;
    setLoading(true);
    try {
      const response = await api.searchDocuments(query.trim(), [...selectedIds]);
      setResults(response.results);
      setSearched(true);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="view-container">
      <div className="view-header">
        <h1 className="view-title">Semantic Search</h1>
        <p className="view-description">Find relevant chunks across your knowledge base by meaning, not keywords.</p>
      </div>

      <div className="chat-view-container" style={{ height: "auto" }}>
        <div>
          <form className="chat-form" onSubmit={handleSubmit}>
            <input
              className="chat-input"
              placeholder="Search your documents…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button className="btn-primary" type="submit" disabled={loading || !query.trim()}>
              <SearchIcon />
            </button>
          </form>

          <div className="search-results">
            {results.map((r, i) => (
              <div key={i} className="search-result-card">
                <div className="search-result-header">
                  <span className="search-result-source">
                    {r.source.document_name} · p.{r.source.page}
                  </span>
                  <span className="search-result-score">{(r.score * 100).toFixed(1)}%</span>
                </div>
                <p className="search-result-content">{r.content}</p>
              </div>
            ))}
            {searched && !loading && results.length === 0 && (
              <div className="no-history-placeholder">No relevant chunks found.</div>
            )}
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
