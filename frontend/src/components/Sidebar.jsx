import { DashboardIcon, KnowledgeBaseIcon, ChatIcon, SearchIcon } from "../icons";

const NAV_ITEMS = [
  { key: "dashboard", label: "Dashboard", Icon: DashboardIcon },
  { key: "knowledgeBase", label: "Knowledge Base", Icon: KnowledgeBaseIcon },
  { key: "chat", label: "Chat", Icon: ChatIcon },
  { key: "search", label: "Search", Icon: SearchIcon },
];

function StatusRow({ label, healthy }) {
  return (
    <div className="status-row">
      <span>{label}</span>
      <span className={`status-indicator`}>
        <span className={`status-dot ${healthy ? "healthy" : "unhealthy"}`} />
        {healthy ? "Online" : "Offline"}
      </span>
    </div>
  );
}

export default function Sidebar({ activeView, onNavigate, health }) {
  return (
    <aside className="sidebar">
      <div className="brand-section">
        <div className="brand-logo" />
        <span className="brand-name">KnowledgeHub AI</span>
      </div>
      <nav className="nav-menu">
        {NAV_ITEMS.map(({ key, label, Icon }) => (
          <button
            key={key}
            type="button"
            className={`nav-item ${activeView === key ? "active" : ""}`}
            onClick={() => onNavigate(key)}
          >
            <Icon />
            {label}
          </button>
        ))}
      </nav>
      <div className="system-status">
        <StatusRow label="Database" healthy={health?.details?.database === "Healthy"} />
        <StatusRow label="Vector Store" healthy={health?.details?.vector_store === "Healthy"} />
        <StatusRow label="Gemini" healthy={health?.details?.gemini === "Healthy"} />
      </div>
    </aside>
  );
}
