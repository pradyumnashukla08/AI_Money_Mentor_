// ─── Core Types ──────────────────────────────────────────────────────────────

export type AgentId = 'manager' | 'auditor' | 'strategist' | 'analyst';

export interface Agent {
  id: AgentId;
  name: string;
  title: string;
  description: string;
  icon: string;
  color: string;
  gradientFrom: string;
  gradientTo: string;
  endpoint: string;
  triggerKeywords: string[];
  capabilities: string[];
}

export interface Message {
  id: string;
  role: 'user' | 'agent';
  content: string;
  agentId: AgentId;
  timestamp: Date;
  attachments?: FileAttachment[];
  routingInfo?: RouteResult;
}

export interface FileAttachment {
  name: string;
  type: string;
  size: number;
  url?: string;
}

export interface RouteResult {
  agent: AgentId;
  confidence: number;
  keywords: string[];
  reasoning: string;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  activeAgent: AgentId;
  createdAt: Date;
  updatedAt: Date;
}

export interface AgentStatus {
  id: AgentId;
  isOnline: boolean;
  currentTask?: string;
  lastActive: Date;
}

export interface QuickAction {
  label: string;
  icon: string;
  targetAgent: AgentId;
  prompt: string;
}
