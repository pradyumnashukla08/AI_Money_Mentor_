"use client";
import React from "react";
import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import { ChatProvider } from "@/context/ChatContext";

export default function NotificationsPage() {
  return (
    <ChatProvider>
      <div className="app-shell">
        <Header />
        <Sidebar />
        <div className="main-content" style={{ overflowY: "auto" }}>
        <div style={{ padding: "var(--sp-10)" }}>
          <h1 style={{ fontFamily: "var(--font-headline)", fontSize: "2rem", marginBottom: "var(--sp-8)" }}>Intelligence Feed</h1>
          <NotificationsContent />
        </div>
        </div>
      </div>
    </ChatProvider>
  );
}

interface NotificationItem {
  id: string;
  title: string;
  message: string;
  type: string;
  isRead: boolean;
  createdAt: string;
}

import { useChat } from "@/context/ChatContext";

function NotificationsContent() {
  const [notifications, setNotifications] = React.useState<NotificationItem[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const { markNotificationsAsRead } = useChat();

  React.useEffect(() => {
    fetch('/api/notifications?markAsRead=true')
      .then(res => res.json())
      .then(data => {
        if (data.notifications) {
          setNotifications(data.notifications);
        }
        setIsLoading(false);
        markNotificationsAsRead();
      })
      .catch(err => {
        console.error(err);
        setIsLoading(false);
      });
  }, []);

  if (isLoading) {
    return <div style={{ color: "var(--outline)" }}>Loading intelligence feed...</div>;
  }

  if (notifications.length === 0) {
    return (
      <div style={{ color: "var(--outline)", padding: "var(--sp-4)", textAlign: "center", background: "var(--glass-bg)", borderRadius: "var(--radius-lg)" }}>
        You have no new notifications. The AI Money Mentor will alert you here when there are updates on your portfolio, tax deadlines, or market insights.
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "var(--sp-4)", maxWidth: 800 }}>
      {notifications.map((notif) => {
        let icon = "💡";
        let colorType = "var(--primary)";
        if (notif.type === "alert") { icon = "⚠️"; colorType = "var(--error)"; }
        if (notif.type === "insight") { icon = "📈"; colorType = "var(--agent-analyst)"; }
        if (notif.type === "reminder") { icon = "📅"; colorType = "var(--agent-auditor)"; }

        return (
          <div key={notif.id} style={{
            background: "var(--glass-bg)",
            backdropFilter: "blur(var(--glass-blur))",
            padding: "var(--sp-5)",
            borderRadius: "var(--radius-lg)",
            borderLeft: `4px solid ${colorType}`,
            display: "flex",
            alignItems: "flex-start",
            gap: "var(--sp-4)",
            opacity: notif.isRead ? 0.7 : 1
          }}>
            <div style={{ fontSize: "1.5rem" }}>{icon}</div>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <h3 style={{ margin: 0, fontWeight: 600, color: "var(--on-surface)" }}>{notif.title}</h3>
                <span style={{ fontSize: "0.75rem", color: "var(--outline)" }}>
                  {new Date(notif.createdAt).toLocaleDateString()}
                </span>
              </div>
              <p style={{ margin: "4px 0 0", color: "var(--on-surface-variant)", fontSize: "0.875rem", whiteSpace: "pre-wrap" }}>
                {notif.message}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
