"use client";
import React, { useEffect, useState, Suspense } from "react";
import { signIn, useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import Link from "next/link";

function SignUpContent() {
  const { status } = useSession();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  useEffect(() => {
    if (status === "authenticated") {
      router.push("/");
    }
  }, [status, router]);

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/auth/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.message || "Something went wrong");
      }

      // Auto login after signup
      const signInRes = await signIn("credentials", {
        email,
        password,
        redirect: false,
      });

      if (signInRes?.error) {
        throw new Error(signInRes.error);
      }

      router.push("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred during sign up");
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setIsLoading(true);
    await signIn("google", { callbackUrl: "/" });
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "var(--surface-base)",
        position: "relative",
        overflow: "hidden",
        fontFamily: "var(--font-body)",
        color: "var(--on-surface)",
      }}
    >
      <div
        style={{
          position: "absolute",
          top: "10%",
          left: "20%",
          width: 500,
          height: 500,
          background: "var(--primary)",
          filter: "blur(180px)",
          opacity: 0.05,
          borderRadius: "50%",
          pointerEvents: "none",
        }}
      />
      
      <div
        style={{
          background: "var(--glass-bg)",
          backdropFilter: "blur(var(--glass-blur))",
          WebkitBackdropFilter: "blur(var(--glass-blur))",
          padding: "var(--sp-12) var(--sp-10)",
          borderRadius: "var(--radius-xl)",
          boxShadow: "var(--shadow-lg)",
          width: "100%",
          maxWidth: 440,
          border: "1px solid var(--glass-border)",
          borderTop: "1px solid rgba(240, 185, 11, 0.2)",
          position: "relative",
          zIndex: 1,
        }}
      >
        <div style={{ textAlign: "center", marginBottom: "var(--sp-8)" }}>
          <div
            style={{
              width: 56,
              height: 56,
              background: "var(--gradient-gold)",
              borderRadius: "var(--radius-lg)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto var(--sp-4)",
              boxShadow: "var(--shadow-glow-gold)",
            }}
          >
            <span style={{ fontSize: "1.75rem", color: "var(--on-primary)" }}>
              🏛️
            </span>
          </div>
          <h1
            style={{
              fontFamily: "var(--font-headline)",
              fontSize: "1.75rem",
              fontWeight: 700,
              color: "var(--on-surface)",
              marginBottom: "var(--sp-1)",
              letterSpacing: "-0.02em",
            }}
          >
            Create an Account
          </h1>
          <p
            style={{
              color: "var(--outline)",
              fontSize: "0.875rem",
              letterSpacing: "0.02em",
            }}
          >
            Join AI Money Mentor for premium financial advice.
          </p>
        </div>

        {error && (
          <div
            style={{
              color: "var(--error-container)",
              background: "rgba(255, 180, 171, 0.1)",
              padding: "var(--sp-3)",
              borderRadius: "var(--radius-md)",
              fontSize: "0.85rem",
              marginBottom: "var(--sp-5)",
              textAlign: "center",
              border: "1px solid var(--error-container)",
            }}
          >
            {error}
          </div>
        )}

        <form onSubmit={handleSignUp} style={{ display: "flex", flexDirection: "column", gap: "var(--sp-4)" }}>
          <div>
            <label style={{ display: "block", marginBottom: "var(--sp-2)", fontSize: "0.875rem", color: "var(--on-surface)" }}>
              Name
            </label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              style={{
                width: "100%",
                padding: "var(--sp-3)",
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--glass-border)",
                background: "rgba(255, 255, 255, 0.05)",
                color: "var(--on-surface)",
                fontSize: "1rem"
              }}
              placeholder="Your Name"
            />
          </div>
          <div>
            <label style={{ display: "block", marginBottom: "var(--sp-2)", fontSize: "0.875rem", color: "var(--on-surface)" }}>
              Email
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{
                width: "100%",
                padding: "var(--sp-3)",
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--glass-border)",
                background: "rgba(255, 255, 255, 0.05)",
                color: "var(--on-surface)",
                fontSize: "1rem"
              }}
              placeholder="your@email.com"
            />
          </div>
          <div>
            <label style={{ display: "block", marginBottom: "var(--sp-2)", fontSize: "0.875rem", color: "var(--on-surface)" }}>
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: "100%",
                padding: "var(--sp-3)",
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--glass-border)",
                background: "rgba(255, 255, 255, 0.05)",
                color: "var(--on-surface)",
                fontSize: "1rem"
              }}
              placeholder="••••••••"
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || status === "loading"}
            style={{
              width: "100%",
              padding: "var(--sp-3)",
              background: "var(--primary)",
              color: "var(--on-primary)",
              border: "none",
              borderRadius: "var(--radius-md)",
              fontFamily: "var(--font-body)",
              fontWeight: 600,
              fontSize: "1rem",
              cursor: isLoading ? "not-allowed" : "pointer",
              boxShadow: "var(--shadow-sm)",
              transition: "all var(--transition-fast)",
              opacity: isLoading ? 0.8 : 1,
              marginTop: "var(--sp-2)",
            }}
          >
            {isLoading ? "Creating account..." : "Sign Up"}
          </button>
        </form>

        <div style={{ margin: "var(--sp-6) 0", display: "flex", alignItems: "center", textTransform: "uppercase", fontSize: "0.75rem", color: "var(--outline)" }}>
          <div style={{ flex: 1, height: 1, backgroundColor: "var(--glass-border)" }} />
          <span style={{ margin: "0 var(--sp-3)" }}>Or</span>
          <div style={{ flex: 1, height: 1, backgroundColor: "var(--glass-border)" }} />
        </div>

        <button
          onClick={handleGoogleLogin}
          disabled={isLoading || status === "loading"}
          style={{
            width: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "12px",
            padding: "var(--sp-3)",
            background: "rgba(255, 255, 255, 0.1)",
            color: "var(--on-surface)",
            border: "1px solid var(--glass-border)",
            borderRadius: "var(--radius-md)",
            fontFamily: "var(--font-body)",
            fontWeight: 600,
            fontSize: "1rem",
            cursor: isLoading ? "not-allowed" : "pointer",
            boxShadow: "var(--shadow-sm)",
            transition: "all var(--transition-fast)",
            opacity: isLoading ? 0.8 : 1,
          }}
          onMouseEnter={(e) => {
            if (!isLoading) {
              e.currentTarget.style.background = "rgba(255, 255, 255, 0.15)";
            }
          }}
          onMouseLeave={(e) => {
            if (!isLoading) {
              e.currentTarget.style.background = "rgba(255, 255, 255, 0.1)";
            }
          }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            <path d="M1 1h22v22H1z" fill="none"/>
          </svg>
          Continue with Google
        </button>

        <div style={{ marginTop: "var(--sp-6)", textAlign: "center", fontSize: "0.875rem", color: "var(--outline)" }}>
          Already have an account?{" "}
          <Link href="/login" style={{ color: "var(--primary)", textDecoration: "none", fontWeight: 600 }}>
            Login here
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function SignUpPage() {
  return (
    <Suspense fallback={<div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--surface-base)", color: "var(--on-surface)" }}>Loading...</div>}>
      <SignUpContent />
    </Suspense>
  );
}
