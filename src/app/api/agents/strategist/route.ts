import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from "next-auth/next";
import { authOptions } from "../../auth/[...nextauth]/route";
import { prisma } from "@/lib/prisma";

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    const body = await request.json();
    const { messages } = body;

    if (!messages || messages.length === 0) {
      return NextResponse.json({ error: "Messages are required" }, { status: 400 });
    }

    const lastMessage = messages[messages.length - 1];
    if (lastMessage.role !== 'user') {
      return NextResponse.json({ error: "Expected user message" }, { status: 400 });
    }

    const messageContent = lastMessage.content.toLowerCase();

    // Determine the Stratgeist Intent Based on Keywords
    const isLifeEvent = ["married", "marriage", "baby", "child", "house", "car", "bonus", "hike", "promotion", "job", "lost", "inheritance", "event", "sudden"].some(kw => messageContent.includes(kw));

    let financialContext = {
      name: session?.user?.name || "User",
      age: 30, // Default baseline for models if unset
      monthly_income: 100000,
      monthly_expenses: 40000,
      current_savings: 500000,
      existing_monthly_sip: 20000,
      risk_tolerance: "moderate",
      life_stage: "early_career",
    };

    // If logged in, fetch exact DB Profile
    if (session?.user?.id) {
      const profile = await prisma.financialProfile.findUnique({
        where: { userId: session.user.id }
      });
      if (profile) {
        financialContext = {
          ...financialContext,
          monthly_income: profile.monthlyIncome,
          monthly_expenses: profile.monthlyIncome * 0.5, // Computed baseline
          current_savings: profile.totalAssets,
          risk_tolerance: profile.riskTolerance.toLowerCase(),
        };
      }
    }

    let backendEndpoint = "";
    let payload: any = {};

    if (isLifeEvent) {
      backendEndpoint = "http://localhost:8000/strategist/life-event";
      payload = {
        profile: financialContext,
        event_text: lastMessage.content
      };
    } else {
      backendEndpoint = "http://localhost:8000/strategist/fire-plan";
      payload = {
        profile: financialContext,
        goal: {
          target_retirement_age: 50,
          desired_monthly_expense: financialContext.monthly_expenses * 1.5, // Buffer for FIRE
          withdrawal_rate: 0.04
        }
      };
    }

    // Proxy out to Python FastApi
    const response = await fetch(backendEndpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
        throw new Error(`Upstream Python API failed with HTTP ${response.status}`);
    }

    const data = await response.json();

    // Construct the formatted markdown response
    let finalResponseString = "";

    if (isLifeEvent) {
        const amount = data.event?.amount || 0;
        finalResponseString += `### 💡 Event Recognized: ${data.event?.event_type?.replace('_', ' ') || 'Unknown'}\n`;
        if (amount > 0) finalResponseString += `Calculated financial impact: **₹${amount.toLocaleString('en-IN')}**\n\n`;
        
        finalResponseString += `${data.risk_assessment}\n\n`;
        finalResponseString += `**Action Plan:**\n`;
        (data.immediate_actions || []).forEach((a: string) => finalResponseString += `- ${a}\n`);
        (data.short_term_plan || []).forEach((p: string) => finalResponseString += `- ${p}\n`);
        
        if (data.long_term_impact) finalResponseString += `\n**Long Term Impact:**\n${data.long_term_impact}\n\n`;
        finalResponseString += `*${data.narrative}*`;
    } else {
        const fireCorpus = data.fire_target?.corpus_at_retirement || 0;
        finalResponseString += `### 🔥 FIRE Roadmap Matrix\n`;
        if (fireCorpus > 0) finalResponseString += `Target Corpus Needed: **₹${fireCorpus.toLocaleString('en-IN')}**\n\n`;
        
        finalResponseString += `${data.narrative}`;
    }

    return NextResponse.json({
      success: true,
      message: finalResponseString,
      timestamp: new Date().toISOString(),
    });

  } catch (error) {
    console.error('Strategist Backend Error:', error);
    return NextResponse.json(
      { error: 'Failed to communicate with the local Python backend engine. Make sure uvicorn is running on :8000', message: 'The local python server is down.' },
      { status: 500 }
    );
  }
}
