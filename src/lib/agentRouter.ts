import { AgentId, RouteResult } from './types';
import { AGENTS } from './agentConfig';

// ─── Agent Router ────────────────────────────────────────────────────────────
// A multi-signal intent classifier that routes user messages to the most
// appropriate specialist agent. Uses weighted keyword matching + contextual
// boosting for accurate routing.

interface ScoredRoute {
  agentId: AgentId;
  score: number;
  matchedKeywords: string[];
}

// File-type associations for upload routing
const FILE_ROUTE_MAP: Record<string, AgentId> = {
  'form16': 'auditor',
  'form 16': 'auditor',
  'salary': 'auditor',
  'itr': 'auditor',
  'cams': 'analyst',
  'kfintech': 'analyst',
  'cas': 'analyst',
  'portfolio': 'analyst',
  'mutual fund': 'analyst',
};

/**
 * Normalizes input text for consistent matching:
 * - lowercase, trim, collapse whitespace
 * - expand common financial abbreviations
 */
function normalizeInput(text: string): string {
  return text
    .toLowerCase()
    .trim()
    .replace(/\s+/g, ' ')
    .replace(/\bmf\b/g, 'mutual fund')
    .replace(/\bnps\b/g, 'national pension scheme')
    .replace(/\belss\b/g, 'equity linked savings scheme')
    .replace(/\betf\b/g, 'exchange traded fund');
}

/**
 * Computes a weighted relevance score for a given agent.
 * - Exact keyword matches get full weight
 * - Partial (substring) matches get half weight
 * - Multi-word keyword phrases get a bonus for exact phrase match
 */
function computeAgentScore(normalizedText: string, agentId: string): ScoredRoute {
  const agent = AGENTS[agentId];
  if (!agent) {
    return { agentId: agentId as AgentId, score: 0, matchedKeywords: [] };
  }

  let score = 0;
  const matchedKeywords: string[] = [];
  const words = normalizedText.split(' ');

  for (const keyword of agent.triggerKeywords) {
    const kwLower = keyword.toLowerCase();
    const isPhrase = kwLower.includes(' ');

    if (isPhrase) {
      // Phrase match: look for exact substring presence
      if (normalizedText.includes(kwLower)) {
        score += 3; // phrases are strong signals
        matchedKeywords.push(keyword);
      }
    } else {
      // Single word match
      if (words.includes(kwLower)) {
        score += 2; // exact word match
        matchedKeywords.push(keyword);
      } else if (normalizedText.includes(kwLower)) {
        score += 1; // substring match (weaker)
        matchedKeywords.push(keyword);
      }
    }
  }

  return { agentId: agentId as AgentId, score, matchedKeywords };
}

/**
 * Main routing function. Classifies the user's message and returns
 * the best matching agent with confidence score.
 *
 * Routing Algorithm:
 * 1. Normalize input text
 * 2. Score each specialist agent by keyword relevance
 * 3. Apply contextual boosts (file mentions, urgency signals)
 * 4. Select highest scorer above threshold; otherwise default to manager
 * 5. Calculate confidence as ratio of top score to total possible
 */
export function routeMessage(
  userMessage: string,
  currentAgent?: AgentId
): RouteResult {
  const normalized = normalizeInput(userMessage);

  // Score each specialist agent (skip manager — it's the fallback)
  const specialists: AgentId[] = ['auditor', 'strategist', 'analyst'];
  const scores: ScoredRoute[] = specialists.map((id) =>
    computeAgentScore(normalized, id)
  );

  // ─── Contextual Boosters ────────────────────────────────────────────
  // Boost for file/upload mentions
  for (const [fileKey, targetAgent] of Object.entries(FILE_ROUTE_MAP)) {
    if (normalized.includes(fileKey)) {
      const match = scores.find((s) => s.agentId === targetAgent);
      if (match) {
        match.score += 4; // strong signal: user mentioned a specific document type
        if (!match.matchedKeywords.includes(fileKey)) {
          match.matchedKeywords.push(fileKey);
        }
      }
    }
  }

  // Boost if user mentions "upload", "attach", "file", "document"
  const uploadWords = ['upload', 'attach', 'file', 'document', 'pdf', 'statement'];
  const hasUploadIntent = uploadWords.some((w) => normalized.includes(w));
  if (hasUploadIntent) {
    // If uploading, boost auditor and analyst (document-heavy agents)
    const auditorScore = scores.find((s) => s.agentId === 'auditor');
    const analystScore = scores.find((s) => s.agentId === 'analyst');
    if (auditorScore && auditorScore.score > 0) auditorScore.score += 2;
    if (analystScore && analystScore.score > 0) analystScore.score += 2;
  }

  // ─── Select Best Agent ──────────────────────────────────────────────
  scores.sort((a, b) => b.score - a.score);
  const topScore = scores[0];

  // Confidence threshold: require at least 2 points to route away from manager
  const ROUTING_THRESHOLD = 2;

  if (topScore.score >= ROUTING_THRESHOLD) {
    // Calculate confidence as a percentage (capped at 1.0)
    const maxPossibleScore = topScore.matchedKeywords.length * 3;
    const confidence = Math.min(topScore.score / Math.max(maxPossibleScore, 1), 1.0);

    return {
      agent: topScore.agentId,
      confidence: Math.round(confidence * 100) / 100,
      keywords: topScore.matchedKeywords,
      reasoning: `Routed to ${AGENTS[topScore.agentId].name} based on ${topScore.matchedKeywords.length} keyword match(es): "${topScore.matchedKeywords.join('", "')}"`,
    };
  }

  // Default: stay with current agent or fallback to manager
  return {
    agent: currentAgent || 'manager',
    confidence: 0.1,
    keywords: [],
    reasoning:
      'No strong specialist match found. Handling with the Manager Agent for general assistance.',
  };
}

/**
 * Routes based on uploaded file type.
 * Examines filename and MIME type to determine which agent should process it.
 */
export function routeFileUpload(
  fileName: string,
  mimeType: string
): RouteResult {
  const nameLower = fileName.toLowerCase();

  // Check filename against known document patterns
  for (const [pattern, agentId] of Object.entries(FILE_ROUTE_MAP)) {
    if (nameLower.includes(pattern.replace(' ', ''))) {
      return {
        agent: agentId,
        confidence: 0.9,
        keywords: [pattern],
        reasoning: `File "${fileName}" matches ${pattern} pattern → routed to ${AGENTS[agentId].name}`,
      };
    }
  }

  // PDF files default to auditor (most common use case: Form 16)
  if (mimeType === 'application/pdf' || nameLower.endsWith('.pdf')) {
    return {
      agent: 'auditor',
      confidence: 0.5,
      keywords: ['pdf'],
      reasoning:
        'PDF file detected. Defaulting to Tax Auditor for document processing.',
    };
  }

  // Fallback
  return {
    agent: 'manager',
    confidence: 0.2,
    keywords: [],
    reasoning: 'Could not determine file type. Manager will assist.',
  };
}
