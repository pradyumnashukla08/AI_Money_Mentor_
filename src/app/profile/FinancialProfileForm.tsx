"use client";

import React, { useState, useEffect } from "react";

export function FinancialProfileForm() {
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [healthScore, setHealthScore] = useState<any>(null);

  const [formData, setFormData] = useState({
    monthlyIncome: "",
    totalAssets: "",
    riskTolerance: "moderate",
    goals: "",
  });

  useEffect(() => {
    fetch("/api/profile")
      .then((res) => res.json())
      .then((data) => {
        if (data.profile) {
          setFormData({
            monthlyIncome: data.profile.monthlyIncome.toString(),
            totalAssets: data.profile.totalAssets.toString(),
            riskTolerance: data.profile.riskTolerance,
            goals: data.profile.goals || "",
          });
        }
        setIsLoading(false);
      })
      .catch((err) => {
        console.error("Error loading profile:", err);
        setIsLoading(false);
      });
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setMessage("");

    try {
      const res = await fetch("/api/profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!res.ok) throw new Error("Failed to save profile");
      
      // Implicitly ping the Python mathematical Health-Score generator using parsed layout defaults
      try {
        const dummyAnswers = {
          answers: { "q1": 0, "q2": 1, "q3": formData.riskTolerance === "high" ? 2 : 0, "q4": 1, "q5": 0, "q6": 0 },
          monthly_income: parseInt(formData.monthlyIncome) || null
        };
        
        const hsRes = await fetch("http://127.0.0.1:8000/api/health-score/calculate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(dummyAnswers),
        });
        
        if (hsRes.ok) {
          const data = await hsRes.json();
          if (data.health_score) setHealthScore(data.health_score);
        }
      } catch (err) {
        console.error("Health score backend fetch securely failed:", err);
      }

      setMessage("Profile saved successfully.");
      setTimeout(() => setMessage(""), 3000);
    } catch {
      setMessage("Error saving profile. Please try again.");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return <div style={{ color: "var(--outline)" }}>Loading financial settings...</div>;
  }

  return (
    <div
      style={{
        background: "var(--glass-bg)",
        backdropFilter: "blur(var(--glass-blur))",
        border: "1px solid var(--glass-border)",
        borderRadius: "var(--radius-xl)",
        padding: "var(--sp-8)",
        boxShadow: "var(--shadow-md)",
      }}
    >
      <h2 style={{ fontSize: "1.25rem", fontWeight: 600, margin: "0 0 var(--sp-6) 0", color: "var(--on-surface)", borderBottom: "1px solid var(--glass-border)", paddingBottom: "var(--sp-4)" }}>
        Financial Settings
      </h2>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "var(--sp-4)" }}>
        <div style={{ display: "flex", gap: "var(--sp-4)", flexWrap: "wrap" }}>
          <div style={{ flex: "1 1 calc(50% - var(--sp-2))" }}>
            <label style={{ display: "block", marginBottom: "var(--sp-2)", fontSize: "0.875rem", color: "var(--on-surface-variant)" }}>
              Monthly Income ($)
            </label>
            <input
              type="number"
              value={formData.monthlyIncome}
              onChange={(e) => setFormData({ ...formData, monthlyIncome: e.target.value })}
              style={{
                width: "100%",
                padding: "var(--sp-3)",
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--glass-border)",
                background: "rgba(255, 255, 255, 0.05)",
                color: "var(--on-surface)",
                fontSize: "1rem"
              }}
              placeholder="0.00"
            />
          </div>
          <div style={{ flex: "1 1 calc(50% - var(--sp-2))" }}>
            <label style={{ display: "block", marginBottom: "var(--sp-2)", fontSize: "0.875rem", color: "var(--on-surface-variant)" }}>
              Total Assets ($)
            </label>
            <input
              type="number"
              value={formData.totalAssets}
              onChange={(e) => setFormData({ ...formData, totalAssets: e.target.value })}
              style={{
                width: "100%",
                padding: "var(--sp-3)",
                borderRadius: "var(--radius-md)",
                border: "1px solid var(--glass-border)",
                background: "rgba(255, 255, 255, 0.05)",
                color: "var(--on-surface)",
                fontSize: "1rem"
              }}
              placeholder="0.00"
            />
          </div>
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "var(--sp-2)", fontSize: "0.875rem", color: "var(--on-surface-variant)" }}>
            Risk Tolerance
          </label>
          <select
            value={formData.riskTolerance}
            onChange={(e) => setFormData({ ...formData, riskTolerance: e.target.value })}
            style={{
              width: "100%",
              padding: "var(--sp-3)",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--glass-border)",
              background: "rgba(255, 255, 255, 0.05)",
              color: "var(--on-surface)",
              fontSize: "1rem"
            }}
          >
            <option value="low" style={{ color: "black" }}>Conservative (Low Risk)</option>
            <option value="moderate" style={{ color: "black" }}>Moderate (Medium Risk)</option>
            <option value="high" style={{ color: "black" }}>Aggressive (High Risk)</option>
          </select>
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "var(--sp-2)", fontSize: "0.875rem", color: "var(--on-surface-variant)" }}>
            Financial Goals
          </label>
          <textarea
            value={formData.goals}
            onChange={(e) => setFormData({ ...formData, goals: e.target.value })}
            rows={3}
            style={{
              width: "100%",
              padding: "var(--sp-3)",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--glass-border)",
              background: "rgba(255, 255, 255, 0.05)",
              color: "var(--on-surface)",
              fontSize: "1rem",
              resize: "vertical"
            }}
            placeholder="e.g. Save for a house, Retire early..."
          />
        </div>

        <button
          type="submit"
          disabled={isSaving}
          style={{
            alignSelf: "flex-start",
            padding: "var(--sp-3) var(--sp-6)",
            background: "var(--primary)",
            color: "var(--on-primary)",
            border: "none",
            borderRadius: "var(--radius-md)",
            fontFamily: "var(--font-body)",
            fontWeight: 600,
            fontSize: "1rem",
            cursor: isSaving ? "not-allowed" : "pointer",
            boxShadow: "var(--shadow-sm)",
            transition: "all var(--transition-fast)",
            opacity: isSaving ? 0.8 : 1,
            marginTop: "var(--sp-2)",
          }}
        >
          {isSaving ? "Saving..." : "Save Settings"}
        </button>

        {message && (
          <p style={{ margin: "var(--sp-2) 0 0 0", fontSize: "0.875rem", color: message.includes("Error") ? "var(--error)" : "var(--agent-auditor)" }}>
            {message}
          </p>
        )}

        {healthScore && (
          <div style={{ marginTop: "var(--sp-6)", padding: "var(--sp-4)", border: `1px solid ${healthScore.overall_band_color}`, borderRadius: "var(--radius-md)", background: "rgba(255, 255, 255, 0.05)" }}>
            <h3 style={{ fontSize: "1.1rem", margin: "0 0 var(--sp-2) 0", color: healthScore.overall_band_color }}>
              Overall Health Score: {healthScore.overall_score}/100
            </h3>
            <p style={{ color: "var(--on-surface-variant)", fontSize: "0.9rem", margin: "0 0 var(--sp-4) 0" }}>
              {healthScore.executive_summary}
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "var(--sp-4)" }}>
              {healthScore.dimension_scores.map((d: any, idx: number) => (
                 <div key={idx} style={{ background: "rgba(0,0,0,0.2)", padding: "var(--sp-3)", borderRadius: "var(--radius-sm)", borderLeft: `3px solid ${d.band_color}` }}>
                    <strong style={{ color: "var(--on-surface)", display: "block", fontSize: "0.9rem" }}>{d.dimension.replace(/_/g, ' ').toUpperCase()}</strong>
                    <span style={{ fontSize: "0.85rem", color: d.band_color }}>Score: {d.score}/14 ({d.band_label})</span>
                 </div>
              ))}
            </div>
          </div>
        )}
      </form>
    </div>
  );
}
