"use client";
import { signOut } from "next-auth/react";

export function SignOutButton() {
  return (
    <button
      onClick={() => signOut({ callbackUrl: "/login" })}
      style={{
        background: "rgba(255, 60, 60, 0.1)",
        color: "#ff6b6b",
        border: "1px solid rgba(255, 60, 60, 0.3)",
        padding: "8px 16px",
        borderRadius: "var(--radius-md)",
        fontWeight: 600,
        cursor: "pointer",
        transition: "all 0.2s ease",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = "rgba(255, 60, 60, 0.2)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = "rgba(255, 60, 60, 0.1)";
      }}
    >
      Sign Out
    </button>
  );
}
