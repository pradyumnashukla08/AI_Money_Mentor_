'use client';
import React from 'react';
import { Message } from '@/lib/types';
import { getAgent } from '@/lib/agentConfig';

interface MessageBubbleProps {
  message: Message;
}

/**
 * Formats message content with basic markdown-like rendering.
 * Supports: **bold**, *italic*, \n (newlines), and • bullet points
 */
function formatContent(content: string): React.ReactNode[] {
  const lines = content.split('\n');
  return lines.map((line, i) => {
    // Process bold (**text**)
    const parts = line.split(/(\*\*.*?\*\*)/g);
    const formatted = parts.map((part, j) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={j}>{part.slice(2, -2)}</strong>;
      }
      // Process italic (*text*)
      const italicParts = part.split(/(\*.*?\*)/g);
      return italicParts.map((ip, k) => {
        if (ip.startsWith('*') && ip.endsWith('*') && !ip.startsWith('**')) {
          return <em key={`${j}-${k}`}>{ip.slice(1, -1)}</em>;
        }
        return ip;
      });
    });

    return (
      <React.Fragment key={i}>
        {formatted}
        {i < lines.length - 1 && <br />}
      </React.Fragment>
    );
  });
}

function formatTime(date: Date | string | number): string {
  const d = new Date(date);
  return d.toLocaleTimeString('en-IN', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  });
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const agent = getAgent(message.agentId);

  return (
    <div className={`message-row ${isUser ? 'user' : 'agent'}`}>
      {/* Avatar */}
      <div
        className={`message-avatar ${isUser ? 'user-avatar' : ''}`}
        style={isUser ? {} : { background: `${agent.color}22` }}
      >
        {isUser ? 'P' : agent.icon}
      </div>

      {/* Message Body */}
      <div className="message-body">
        {!isUser && (
          <div className="message-header">
            <span className="message-agent-name" style={{ color: agent.color }}>
              {agent.name}
            </span>
            <span
              className="message-badge"
              style={{
                background: `${agent.color}20`,
                color: agent.color,
              }}
            >
              {agent.title}
            </span>
            <span className="message-time">{formatTime(message.timestamp)}</span>
          </div>
        )}

        <div className={`message-bubble ${isUser ? 'user-bubble' : 'agent-bubble'}`}>
          {formatContent(message.content)}
        </div>

        {isUser && (
          <span className="message-time" style={{ textAlign: 'right', paddingRight: '8px' }}>
            {formatTime(message.timestamp)}
          </span>
        )}

        {/* Routing info */}
        {message.routingInfo && message.routingInfo.confidence > 0.3 && (
          <div className="route-tag">
            🧭 Routed → {getAgent(message.routingInfo.agent).name} ({Math.round(message.routingInfo.confidence * 100)}%)
          </div>
        )}
      </div>
    </div>
  );
}
