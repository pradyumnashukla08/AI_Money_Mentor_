'use client';
import React from 'react';
import { useChat } from '@/context/ChatContext';
import { getAllAgents } from '@/lib/agentConfig';
import { useRouter, usePathname } from 'next/navigation';

export default function Sidebar() {
  const { activeAgent, setActiveAgent, sidebarOpen, sessions, clearChat, loadSession, deleteSession } = useChat();
  const agents = getAllAgents();
  const router = useRouter();
  const pathname = usePathname();

  return (
    <aside className={`sidebar ${sidebarOpen ? '' : 'collapsed'}`}>
      {/* Agent Cards */}
      <div className="sidebar-section">
        <div className="sidebar-label">AI Agents</div>
        {agents.map((agent) => (
          <button
            key={agent.id}
            className={`agent-card ${activeAgent === agent.id ? 'active' : ''}`}
            onClick={() => {
              clearChat(agent.id);
              if (pathname !== '/') router.push('/');
            }}
            id={`agent-card-${agent.id}`}
          >
            <div className="agent-icon">
              <div
                className="agent-icon-bg"
                style={{ background: agent.color }}
              />
              <span>{agent.icon}</span>
            </div>
            <div className="agent-info">
              <div className="agent-name" style={activeAgent === agent.id ? { color: agent.color } : {}}>
                {agent.name}
              </div>
              <div className="agent-title">{agent.title}</div>
            </div>
            <div
              className={`agent-status-dot online`}
              style={{ background: agent.color, boxShadow: `0 0 6px ${agent.color}` }}
            />
          </button>
        ))}
      </div>

      {/* Session History */}
      <div className="sidebar-section">
        <div className="sidebar-label">Recent Chats</div>
      </div>
      <div className="sessions-list">
        {sessions.length === 0 && (
          <div className="session-item" style={{ cursor: 'default', opacity: 0.5 }}>
            <span className="session-icon">💬</span>
            <span className="session-title">No previous chats</span>
          </div>
        )}
        {sessions.map((session) => (
          <div 
            key={session.id} 
            className="session-item" 
            id={`session-${session.id}`}
            onClick={() => {
              loadSession(session.id);
              if (pathname !== '/') router.push('/');
            }}
            style={{ cursor: "pointer", display: "flex", justifyContent: "space-between", alignItems: "center" }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "12px", overflow: "hidden" }}>
              <span className="session-icon">💬</span>
              <span className="session-title" style={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{session.title}</span>
            </div>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                deleteSession(session.id);
              }}
              style={{
                background: "transparent",
                border: "none",
                color: "#ff4d4f",
                cursor: "pointer",
                padding: "4px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                borderRadius: "4px",
                opacity: 0.7,
                transition: "opacity 0.2s"
              }}
              onMouseEnter={(e) => e.currentTarget.style.opacity = "1"}
              onMouseLeave={(e) => e.currentTarget.style.opacity = "0.7"}
              title="Delete Chat"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 6h18"></path>
                <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
                <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
              </svg>
            </button>
          </div>
        ))}
      </div>

      {/* New Chat Button */}
      <button 
        className="sidebar-new-chat" 
        onClick={() => {
          clearChat();
          if (pathname !== '/') router.push('/');
        }} 
        id="new-chat-btn"
      >
        <span>＋</span> New Chat
      </button>
    </aside>
  );
}
