const API_BASE = "http://localhost:8000";

async function request(path, options) {
  const res = await fetch(`${API_BASE}${path}`, options);
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const message =
      typeof data?.detail === "string" ? data.detail : data?.detail?.message || "Request failed";
    const error = new Error(message);
    error.status = res.status;
    error.data = data?.detail ?? data;
    throw error;
  }
  return data;
}

const jsonHeaders = { "Content-Type": "application/json" };

export function getDocuments() {
  return request("/documents/");
}

export function deleteDocument(id) {
  return request(`/documents/${id}`, { method: "DELETE" });
}

export function reindexDocument(id) {
  return request(`/documents/${id}/reindex`, { method: "POST" });
}

export function uploadDocument(file, override = false) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("override", String(override));
  return request("/documents/upload", { method: "POST", body: formData });
}

export function askQuestion(question, documentIds) {
  return request("/chat", {
    method: "POST",
    headers: jsonHeaders,
    body: JSON.stringify({ question, document_ids: documentIds?.length ? documentIds : null }),
  });
}

export function getHistory() {
  return request("/history");
}

export function searchDocuments(query, documentIds) {
  return request("/search", {
    method: "POST",
    headers: jsonHeaders,
    body: JSON.stringify({ query, document_ids: documentIds?.length ? documentIds : null }),
  });
}

export function getHealth() {
  return request("/health/");
}

export function getDashboard() {
  return request("/dashboard");
}
