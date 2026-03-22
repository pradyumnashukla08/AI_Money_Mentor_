import { getServerSession } from "next-auth/next";
import { authOptions } from "../api/auth/[...nextauth]/route";
import { redirect } from "next/navigation";
import { prisma } from "@/lib/prisma";
import Image from "next/image";
import Link from "next/link";
import { SignOutButton } from "./SignOutButton";

import { FinancialProfileForm } from "./FinancialProfileForm";

export default async function ProfilePage() {
  const session = await getServerSession(authOptions);

  if (!session?.user) {
    redirect("/login");
  }


  return (
    <div
      style={{
        minHeight: "100vh",
        background: "var(--surface-base)",
        color: "var(--on-surface)",
        padding: "var(--sp-12) var(--sp-6)",
        fontFamily: "var(--font-body)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "800px",
          display: "flex",
          flexDirection: "column",
          gap: "var(--sp-8)",
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1 style={{ fontFamily: "var(--font-headline)", fontSize: "2rem", color: "var(--on-surface)" }}>
            Profile
          </h1>
          <Link href="/">
            <button style={{
              background: "rgba(255, 255, 255, 0.05)",
              border: "1px solid var(--glass-border)",
              color: "var(--on-surface)",
              padding: "8px 16px",
              borderRadius: "var(--radius-md)",
              cursor: "pointer",
            }}>
              Back to Chat
            </button>
          </Link>
        </div>

        {/* User Card */}
        <div
          style={{
            background: "var(--glass-bg)",
            backdropFilter: "blur(var(--glass-blur))",
            border: "1px solid var(--glass-border)",
            borderRadius: "var(--radius-xl)",
            padding: "var(--sp-8)",
            display: "flex",
            alignItems: "center",
            gap: "var(--sp-6)",
            boxShadow: "var(--shadow-md)",
          }}
        >
          <div style={{
            position: "relative",
            width: 80,
            height: 80,
            borderRadius: "50%",
            overflow: "hidden",
            border: "2px solid var(--primary)",
          }}>
            <Image
              src={session.user.image || `https://ui-avatars.com/api/?name=${encodeURIComponent(session.user.name || "User")}&background=random`}
              alt="Profile Picture"
              fill
              style={{ objectFit: 'cover' }}
            />
          </div>
          <div style={{ flex: 1 }}>
            <h2 style={{ fontSize: "1.5rem", fontWeight: 600, margin: 0, color: "var(--on-surface)" }}>
              {session.user.name}
            </h2>
            <p style={{ color: "var(--outline)", fontSize: "0.9rem", marginTop: "4px" }}>
              {session.user.email}
            </p>
          </div>
          <SignOutButton />
        </div>

        <FinancialProfileForm />


      </div>
    </div>
  );
}
