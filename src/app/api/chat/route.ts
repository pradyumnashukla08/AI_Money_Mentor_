import { NextRequest, NextResponse } from 'next/server';
import { routeFileUpload } from '@/lib/agentRouter';
import { AGENTS } from '@/lib/agentConfig';
import { managerAgentGraph } from '@/lib/agents/managerAgent';
import { HumanMessage, AIMessage, SystemMessage } from '@langchain/core/messages';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { messages, hasFile, fileName, fileType } = body;

    if (!messages && !hasFile) {
      return NextResponse.json(
        { error: 'Messages or file is required' },
        { status: 400 }
      );
    }

    // Handle file uploads (bypass LangGraph routing for file uploads usually, or inject as a mock message)
    if (hasFile && fileName) {
      const routeResult = routeFileUpload(fileName, fileType || 'application/pdf');
      const targetAgent = AGENTS[routeResult.agent];
      return NextResponse.json({
        success: true,
        routing: {
          agent: routeResult.agent,
          agentName: targetAgent.name,
          agentTitle: targetAgent.title,
          confidence: routeResult.confidence,
          keywords: routeResult.keywords,
          reasoning: routeResult.reasoning,
        },
        message: `I received your file **${fileName}**. I am handing this over to ${targetAgent.name} to process it.`,
        timestamp: new Date().toISOString(),
      });
    }

    // Convert frontend messages to LangChain messages
    const langchainMessages = messages.map((m: { role: string; content: string }) => {
      if (m.role === 'user') return new HumanMessage(m.content);
      if (m.role === 'agent' || m.role === 'assistant') return new AIMessage(m.content);
      return new SystemMessage(m.content);
    });

    // Invoke the orchestrator graph
    const initialState = {
      messages: langchainMessages,
    };

    const finalState = await managerAgentGraph.invoke(initialState);
    
    // Extract routing info and response
    const targetAgentId = finalState.targetAgent || 'manager';
    const targetAgent = AGENTS[targetAgentId];
    
    let generatedMessage = "";
    if (targetAgentId === 'manager') {
      // The manager responded directly
      const lastMessage = finalState.messages[finalState.messages.length - 1];
      generatedMessage = typeof lastMessage.content === 'string' 
        ? lastMessage.content 
        : JSON.stringify(lastMessage.content);
    } else {
      // It was routed to someone else
      generatedMessage = `I'm handing this over to **${targetAgent.name}** (${targetAgent.title}) to handle your request regarding: *${finalState.routingReasoning}*`;
    }

    return NextResponse.json({
      success: true,
      routing: {
        agent: targetAgentId,
        agentName: targetAgent.name,
        agentTitle: targetAgent.title,
        confidence: 0.9, // Default to high confidence since LLM decided
        keywords: [],
        reasoning: finalState.routingReasoning || "Handled by Manager Agent",
      },
      message: generatedMessage,
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error('Chat API error:', error);
    const errorMessage = error instanceof Error ? error.message : String(error);
    
    let userFriendlyError = 'An unexpected error occurred. Please try again later.';
    if (errorMessage.includes('quota') || errorMessage.includes('429')) {
      userFriendlyError = '⚠️ **Groq API Quota Exceeded**\n\nYour Groq API key has run out of credits. Please check your [Groq Dashboard](https://console.groq.com) to add credits, then try again.';
    } else if (errorMessage.includes('invalid_api_key') || errorMessage.includes('Incorrect API key')) {
      userFriendlyError = '⚠️ **Invalid API Key**\n\nThe Groq API key provided is not valid. Please check your `.env.local` file and ensure it is correct.';
    }

    return NextResponse.json(
      { error: userFriendlyError, message: `System Error: ${errorMessage}` },
      { status: 500 }
    );
  }
}
