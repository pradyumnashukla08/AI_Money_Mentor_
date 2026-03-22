'use client';
import React from 'react';
import { useChat } from '@/context/ChatContext';
import { getAllAgents } from '@/lib/agentConfig';

export default function WelcomeScreen() {
  const { setActiveAgent, sendMessage } = useChat();
  const agents = getAllAgents().filter((a) => a.id !== 'manager');

  const handleAgentClick = (agentId: string) => {
    setActiveAgent(agentId as 'auditor' | 'strategist' | 'analyst');
    sendMessage(`Hi! I'd like to use the ${agentId === 'auditor' ? 'Tax Auditor' : agentId === 'strategist' ? 'Wealth Strategist' : 'Portfolio Analyst'} agent.`);
  };

  return (
    <div className="welcome-container">
      <div className="welcome-glow">🏛️</div>
      <h1 className="welcome-title">Welcome to AI Money Mentor</h1>
      <p className="welcome-subtitle">
        Your AI-powered financial advisor, built for the Indian investor.
        Get personalized tax advice, FIRE planning, portfolio analysis, and
        life event guidance — all in one place.
      </p>

      <div className="welcome-agents">
        {agents.map((agent) => (
          <button
            key={agent.id}
            className="welcome-agent-card"
            onClick={() => handleAgentClick(agent.id)}
            id={`welcome-agent-${agent.id}`}
          >
            <div
              className="welcome-agent-icon"
              style={{ background: `${agent.color}20` }}
            >
              {agent.icon}
            </div>
            <div className="welcome-agent-name" style={{ color: agent.color }}>
              {agent.name}
            </div>
            <div className="welcome-agent-desc">{agent.description}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
