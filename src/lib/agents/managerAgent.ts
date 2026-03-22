import { StateGraph, Annotation } from "@langchain/langgraph";
import { ChatGroq } from "@langchain/groq";
import { BaseMessage, SystemMessage } from "@langchain/core/messages";
import { z } from "zod";

import { AgentId } from "../types";

// ─── Agent State ────────────────────────────────────────────────────────────

export const ManagerStateAnnotation = Annotation.Root({
  messages: Annotation<BaseMessage[]>({
    reducer: (x, y) => x.concat(y),
    default: () => [],
  }),
  targetAgent: Annotation<AgentId | null>({
    reducer: (x, y) => (y !== undefined ? y : x),
    default: () => null,
  }),
  isRouting: Annotation<boolean>({
    reducer: (x, y) => (y !== undefined ? y : x),
    default: () => true,
  }),
  routingReasoning: Annotation<string | null>({
    reducer: (x, y) => (y !== undefined ? y : x),
    default: () => null,
  }),
});

export type ManagerState = typeof ManagerStateAnnotation.State;

// ─── Nodes ──────────────────────────────────────────────────────────────────

// 1. Router Node: Determines which agent should handle the user's intent
async function routerNode(state: ManagerState): Promise<Partial<ManagerState>> {
  const llm = new ChatGroq({
    apiKey: process.env.GROQ_API_KEY || "",
    model: "llama-3.1-8b-instant",
    temperature: 0,
  });

  const lastMessage = state.messages[state.messages.length - 1];
  if (!lastMessage) return {};

  const systemPrompt = `You are Artha, the Manager Agent for AI Money Mentor (an Economic Times themed financial app).
Your job is to analyze the user's input and decide which specialist agent should handle it.
Available Agents:
1. "auditor" (TaxSense): Form 16 uploads, Tax Old vs New regime, Money Health Score, Tax-saving.
2. "strategist" (WealthPath): FIRE planning, SIP/compounding math, Life events (marriage, baby, bonus), inflation.
3. "analyst" (PortfolioX): Mutual Fund CAMS/CAS uploads, XIRR returns, Portfolio overlap, Couple's optimize.
4. "manager": General financial Q&A, greetings, onboarding, or if no other agent fits.

If the user mentions an uploaded file (like PDF or Form 16), strongly bias towards "auditor" or "analyst" based on keywords.`;

  // Use structured output for the LLM to return routing info
  const routingSchema = z.object({
    agent: z.enum(["manager", "auditor", "strategist", "analyst"]),
    confidence: z.number().min(0).max(1),
    reasoning: z.string(),
  });

  const structuredLlm = llm.withStructuredOutput(routingSchema, {
    name: "route_query",
  });

  const routerResult = await structuredLlm.invoke([
    new SystemMessage(systemPrompt),
    ...state.messages,
  ]);

  return {
    targetAgent: routerResult.agent as AgentId,
    routingReasoning: routerResult.reasoning,
    isRouting: false,
  };
}

// 2. Manager Responder Node (If the query is meant for the manager)
async function managerResponderNode(state: ManagerState): Promise<Partial<ManagerState>> {
  const llm = new ChatGroq({
    apiKey: process.env.GROQ_API_KEY || "",
    model: "llama-3.1-8b-instant",
    temperature: 0.7,
  });

  const systemPrompt = `You are Artha, the financial concierge for AI Money Mentor. 
Answer the user's general finance question or greet them proactively. Keep responses short, concise, and professional, maintaining a premium "Economic Times" tone. Use markdown. Do not answer deep tax questions or portfolio overlaps—remind the user that the Auditor or Analyst can handle those.`;

  const response = await llm.invoke([
    new SystemMessage(systemPrompt),
    ...state.messages,
  ]);

  return {
    messages: [response],
  };
}

// ─── Conditional Edges ──────────────────────────────────────────────────────

function routeAfterAnalysis(state: ManagerState) {
  // If we decided it belongs to the manager, run the manager logic
  if (state.targetAgent === "manager") {
    return "managerResponder";
  }
  // If it's another agent, end the graph (the caller will forward to that agent)
  return "__end__";
}

// ─── Graph Definition ───────────────────────────────────────────────────────

export const createManagerGraph = () => {
  const graph = new StateGraph(ManagerStateAnnotation)
    .addNode("router", routerNode)
    .addNode("managerResponder", managerResponderNode)
    // The graph starts by analyzing intent
    .addEdge("__start__", "router")
    // Then conditionally routes
    .addConditionalEdges("router", routeAfterAnalysis)
    // If it goes to the manager, it ends after responding
    .addEdge("managerResponder", "__end__");

  return graph.compile();
};

export const managerAgentGraph = createManagerGraph();
