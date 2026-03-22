"use client";
import React from "react";

import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import { ChatProvider } from "@/context/ChatContext";

export default function SearchPage() {
  return (
    <ChatProvider>
      <div className="app-shell">
        <Header />
        <Sidebar />
        <div className="main-content" style={{ overflowY: "auto" }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 'calc(100vh - 64px)', padding: 'var(--sp-6)' }}>
          <div style={{
            background: "var(--glass-bg)",
            backdropFilter: "blur(var(--glass-blur))",
            WebkitBackdropFilter: "blur(var(--glass-blur))",
            padding: "var(--sp-12)",
            borderRadius: "var(--radius-xl)",
            border: "1px solid var(--glass-border)",
            textAlign: "center",
            maxWidth: 600,
            width: "100%",
            boxShadow: "var(--shadow-lg)"
          }}>
            <h1 style={{ fontFamily: "var(--font-headline)", fontSize: "2rem", marginBottom: "var(--sp-4)" }}>Search</h1>
            <p style={{ color: "var(--on-surface-variant)", marginBottom: "var(--sp-6)" }}>
              Deep dive into your financial logs, past AI advice, and portfolio insights.
            </p>
            <div style={{ position: "relative" }}>
              <input 
                type="text" 
                placeholder="Query transactions or insights..." 
                style={{
                  width: "100%",
                  padding: "var(--sp-4) var(--sp-5)",
                  background: "var(--surface-lowest)",
                  border: "1px solid transparent",
                  borderBottom: "2px solid rgba(240, 185, 11, 0.1)",
                  borderRadius: "var(--radius-md)",
                  color: "var(--on-surface)",
                  fontFamily: "var(--font-body)",
                  fontSize: "1rem",
                  outline: "none",
                }}
              />
            </div>
          </div>
        </div>
        </div>
      </div>
    </ChatProvider>
  );
}
