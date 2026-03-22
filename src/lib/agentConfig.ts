import { Agent, QuickAction } from './types';

// ─── Agent Definitions ──────────────────────────────────────────────────────
// Each agent corresponds to a team member's domain of expertise.
// The Manager Agent (Person 1) orchestrates and routes to specialists.

export const AGENTS: Record<string, Agent> = {
  manager: {
    id: 'manager',
    name: 'The Orchestrator',
    title: 'Manager Agent',
    description:
      'Your personal financial concierge. I route your queries to the right specialist and help with general financial guidance.',
    icon: '🏛️',
    color: '#f0b90b',
    gradientFrom: '#f0b90b',
    gradientTo: '#ffd87f',
    endpoint: '/api/chat',
    triggerKeywords: ['hello', 'hi', 'help', 'what can you do', 'menu', 'options'],
    capabilities: [
      'Route to specialist agents',
      'General financial Q&A',
      'Onboarding & guidance',
    ],
  },
  auditor: {
    id: 'auditor',
    name: 'The Tax Auditor',
    title: 'Tax Specialist',
    description:
      'Expert in tax optimization. Upload your Form 16 for Old vs New regime comparison. Calculates your Money Health Score.',
    icon: '📊',
    color: '#56ceff',
    gradientFrom: '#56ceff',
    gradientTo: '#b1e4ff',
    endpoint: '/api/agents/auditor',
    triggerKeywords: [
      'tax', 'form 16', 'form16', 'itr', 'income tax', 'old regime', 'new regime',
      'tax saving', '80c', '80d', 'hra', 'deduction', 'health score', 'money health',
      'tax return', 'salary slip', 'tds', 'tax planning', 'section 80',
    ],
    capabilities: [
      'Form 16 OCR & analysis',
      'Old vs New tax regime comparison',
      'Money Health Score calculation',
      'Tax-saving recommendations',
    ],
  },
  strategist: {
    id: 'strategist',
    name: 'The Strategist',
    title: 'Wealth Planner',
    description:
      'Plans your FIRE journey, handles life events, and builds personalized financial roadmaps with SIP & compounding math.',
    icon: '🎯',
    color: '#4ade80',
    gradientFrom: '#4ade80',
    gradientTo: '#86efac',
    endpoint: '/api/agents/strategist',
    triggerKeywords: [
      'fire', 'retire', 'retirement', 'sip', 'compounding', 'savings', 'goal',
      'married', 'marriage', 'baby', 'child', 'house', 'car', 'bonus', 'salary hike',
      'promotion', 'job change', 'inheritance', 'life event', 'emergency fund',
      'insurance', 'term plan', 'roadmap', 'plan', 'inflation', 'budget',
    ],
    capabilities: [
      'FIRE path planning',
      'SIP & compounding calculations',
      'Life event financial advice',
      'Inflation-adjusted roadmaps',
    ],
  },
  analyst: {
    id: 'analyst',
    name: 'The Analyst',
    title: 'Portfolio Specialist',
    description:
      'Analyzes mutual fund portfolios from CAMS/KFintech statements. Calculates XIRR, detects overlaps, and optimizes couple finances.',
    icon: '📈',
    color: '#c084fc',
    gradientFrom: '#c084fc',
    gradientTo: '#e9d5ff',
    endpoint: '/api/agents/analyst',
    triggerKeywords: [
      'portfolio', 'mutual fund', 'mf', 'cams', 'kfintech', 'xirr', 'returns',
      'nav', 'overlap', 'benchmark', 'sip', 'redemption', 'folio', 'amc',
      'couple', 'joint', 'spouse', 'partner', 'combined', 'nps', 'elss',
      'debt fund', 'equity', 'hybrid', 'index fund', 'etf',
    ],
    capabilities: [
      'CAMS/KFintech statement parsing',
      'XIRR & returns calculation',
      'Portfolio overlap detection',
      "Couple's finance optimization",
    ],
  },
};

// ─── Quick Action Chips ─────────────────────────────────────────────────────
export const QUICK_ACTIONS: QuickAction[] = [
  {
    label: 'Upload Form 16',
    icon: '📄',
    targetAgent: 'auditor',
    prompt: 'I want to upload my Form 16 for tax analysis',
  },
  {
    label: 'Plan FIRE',
    icon: '🔥',
    targetAgent: 'strategist',
    prompt: 'Help me create a FIRE (Financial Independence, Retire Early) plan',
  },
  {
    label: 'Life Event',
    icon: '💍',
    targetAgent: 'strategist',
    prompt: 'I have a major life event to discuss',
  },
  {
    label: 'Portfolio X-Ray',
    icon: '🔬',
    targetAgent: 'analyst',
    prompt: 'I want to analyze my mutual fund portfolio',
  },
  {
    label: "Couple's Plan",
    icon: '👫',
    targetAgent: 'analyst',
    prompt: "Help us optimize our combined finances as a couple",
  },
  {
    label: 'Health Score',
    icon: '💪',
    targetAgent: 'auditor',
    prompt: 'Calculate my Money Health Score',
  },
];

export const getAgent = (id: string): Agent => {
  return AGENTS[id] || AGENTS.manager;
};

export const getAllAgents = (): Agent[] => {
  return Object.values(AGENTS);
};
