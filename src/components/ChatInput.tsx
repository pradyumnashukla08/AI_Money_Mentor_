'use client';
import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '@/context/ChatContext';
import { QUICK_ACTIONS, getAgent } from '@/lib/agentConfig';

import HealthScoreModal from './HealthScoreModal';
import FirePlanModal from './FirePlanModal';
import LifeEventModal from './LifeEventModal';
import CouplePlanModal from './CouplePlanModal';

export default function ChatInput() {
  const { sendMessage, handleFileUpload, activeAgent, isLoading, messages } = useChat();
  const [input, setInput] = useState('');
  const [isHealthModalOpen, setIsHealthModalOpen] = useState(false);
  const [isFireModalOpen, setIsFireModalOpen] = useState(false);
  const [isLifeEventModalOpen, setIsLifeEventModalOpen] = useState(false);
  const [isCoupleModalOpen, setIsCoupleModalOpen] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const agent = getAgent(activeAgent);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 120) + 'px';
    }
  }, [input]);

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;
    sendMessage(trimmed);
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileUpload(file);
      e.target.value = '';
    }
  };

  const handleQuickAction = (prompt: string, label: string) => {
    if (label === 'Health Score') {
      setIsHealthModalOpen(true);
    } else if (label === 'Plan FIRE') {
      setIsFireModalOpen(true);
    } else if (label === 'Life Event') {
      setIsLifeEventModalOpen(true);
    } else if (label === "Couple's Plan") {
      setIsCoupleModalOpen(true);
    } else {
      sendMessage(prompt);
    }
  };

  const onHealthScoreComplete = (scoreData: any) => {
    setIsHealthModalOpen(false);
    const msg = `### 💚 Money Health Score: ${scoreData.overall_score}/100
    
*   **Result:** <span style="color:${scoreData.overall_band_color};font-weight:bold">${scoreData.overall_band_label}</span>
*   **Diagnosis:** ${scoreData.executive_summary}

**Top Highlights:** ${scoreData.top_strengths[0]}
**Focus Area:** ${scoreData.top_concerns[0]}`;

    sendMessage(msg);
  };

  const onFirePlanComplete = (data: any) => {
    setIsFireModalOpen(false);
    const fireCorpus = data.fire_target?.corpus_at_retirement || 0;
    const msg = `### 🔥 F.I.R.E. Matrix Target Generated
    
Required Retirement Corpus: **₹${fireCorpus.toLocaleString('en-IN')}**

**The Strategist's Analysis:**
${data.narrative}`;

    sendMessage(msg);
  };

  const onLifeEventComplete = (data: any) => {
    setIsLifeEventModalOpen(false);
    const amount = data.event?.amount || 0;
    let msg = `### 💍 Life Event Modeler: ${data.event?.event_type?.replace('_', ' ') || 'Registered'}\n`;
    if (amount > 0) msg += `Calculated financial impact: **₹${amount.toLocaleString('en-IN')}**\n\n`;
    
    msg += `${data.risk_assessment}\n\n**Action Plan:**\n`;
    (data.immediate_actions || []).forEach((a: string) => msg += `- ${a}\n`);
    (data.short_term_plan || []).forEach((p: string) => msg += `- ${p}\n`);
    
    if (data.long_term_impact) msg += `\n**Long Term Impact:**\n${data.long_term_impact}\n\n`;
    msg += `*${data.narrative}*`;

    sendMessage(msg);
  };

  const onCoupleComplete = (data: any) => {
    setIsCoupleModalOpen(false);
    sendMessage(data.message);
  };

  const showQuickActions = messages.length === 0;

  return (
    <>
      <HealthScoreModal 
        isOpen={isHealthModalOpen} 
        onClose={() => setIsHealthModalOpen(false)} 
        onComplete={onHealthScoreComplete} 
      />
      <FirePlanModal 
        isOpen={isFireModalOpen} 
        onClose={() => setIsFireModalOpen(false)} 
        onComplete={onFirePlanComplete} 
      />
      <LifeEventModal
        isOpen={isLifeEventModalOpen}
        onClose={() => setIsLifeEventModalOpen(false)}
        onComplete={onLifeEventComplete}
      />
      <CouplePlanModal
        isOpen={isCoupleModalOpen}
        onClose={() => setIsCoupleModalOpen(false)}
        onComplete={onCoupleComplete}
      />
      <div className="chat-input-area">
        {showQuickActions && (
          <div className="quick-actions">
            {QUICK_ACTIONS.map((action) => (
              <button
                key={action.label}
                className="quick-chip"
                onClick={() => handleQuickAction(action.prompt, action.label)}
                id={`quick-action-${action.label.toLowerCase().replace(/\s+/g, '-')}`}
              >
                <span className="quick-chip-icon">{action.icon}</span>
                {action.label}
              </button>
            ))}
          </div>
        )}

      <div className="input-container">
        <button
          className="input-file-btn"
          onClick={() => fileInputRef.current?.click()}
          aria-label="Upload file"
          id="file-upload-btn"
        >
          📎
        </button>
        <input
          ref={fileInputRef}
          type="file"
          className="input-file-hidden"
          accept=".pdf,.png,.jpg,.jpeg,.csv,.xlsx"
          onChange={handleFile}
          id="file-input"
        />

        <textarea
          ref={textareaRef}
          className="input-textarea"
          placeholder={`Message ${agent.name}...`}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          disabled={isLoading}
          id="chat-input"
        />

        <button
          className="input-send-btn"
          onClick={handleSubmit}
          disabled={!input.trim() || isLoading}
          aria-label="Send message"
          id="send-btn"
        >
          ↗
        </button>
      </div>

      <div className="active-agent-indicator">
        <span
          className="active-agent-dot"
          style={{ background: agent.color, boxShadow: `0 0 6px ${agent.color}` }}
        />
        Talking to {agent.name} — {agent.title}
      </div>
    </div>
    </>
  );
}
