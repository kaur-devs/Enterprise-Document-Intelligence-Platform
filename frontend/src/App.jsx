import { useCallback, useEffect, useState } from "react";
import * as api from "./api";
import { TERMINAL_STATUSES } from "./utils";
import Sidebar from "./components/Sidebar";
import DashboardView from "./components/DashboardView";
import KnowledgeBase from "./components/KnowledgeBase";
import ChatView from "./components/ChatView";
import SearchView from "./components/SearchView";

export default function App() {
  const [activeView, setActiveView] = useState("dashboard");
  const [documents, setDocuments] = useState([]);
  const [health, setHealth] = useState(null);

  const refreshDocuments = useCallback(async () => {
    const docs = await api.getDocuments();
    setDocuments(docs);
    return docs;
  }, []);

  useEffect(() => {
    refreshDocuments();
    api.getHealth().then(setHealth).catch(() => setHealth(null));
    const healthInterval = setInterval(() => {
      api.getHealth().then(setHealth).catch(() => setHealth(null));
    }, 20000);
    return () => clearInterval(healthInterval);
  }, [refreshDocuments]);

  useEffect(() => {
    const hasPending = documents.some((doc) => !TERMINAL_STATUSES.has(doc.status));
    if (!hasPending) return;
    const pollInterval = setInterval(refreshDocuments, 3000);
    return () => clearInterval(pollInterval);
  }, [documents, refreshDocuments]);

  return (
    <div className="app-container">
      <Sidebar activeView={activeView} onNavigate={setActiveView} health={health} />
      <main className="main-content">
        {activeView === "dashboard" && <DashboardView />}
        {activeView === "knowledgeBase" && (
          <KnowledgeBase documents={documents} onRefresh={refreshDocuments} />
        )}
        {activeView === "chat" && <ChatView documents={documents} />}
        {activeView === "search" && <SearchView documents={documents} />}
      </main>
    </div>
  );
}
