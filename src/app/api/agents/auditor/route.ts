import { NextRequest, NextResponse } from 'next/server';
import { ChatGroq } from '@langchain/groq';
import { SystemMessage, HumanMessage } from '@langchain/core/messages';
import { z } from 'zod';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const content = body.messages[body.messages.length - 1].content;
    
    // We instantiate a real ChatGroq module instead of the fake 15L Hardcoded fallback!
    const llm = new ChatGroq({
      apiKey: process.env.GROQ_API_KEY || "",
      model: "llama-3.1-8b-instant",
      temperature: 0,
    });

    const extractionSchema = z.object({
      hasFinancialData: z.boolean().describe("Whether the user has provided their salary/income details."),
      gross_salary: z.number().optional().describe("The user's extracted gross salary. Default to 0 if not provided. Treat 'lakhs' as 100,000."),
      hra_received: z.number().optional(),
      deduction_80c: z.number().optional(),
      deduction_80d: z.number().optional(),
      conversationalReply: z.string().describe("If the user hasn't provided enough financial data to compute their taxes, write a polite greeting asking them for their Gross Salary or to upload their Form 16 PDF. If they have provided data, leave this blank."),
    });

    const structuredLlm = llm.withStructuredOutput(extractionSchema, {
      name: "tax_input_extraction",
    });

    const systemPrompt = `You are The Tax Auditor for AI Money Mentor. The user is chatting with you.
If they just say 'hi' or provide general chat, politely introduce yourself and ask them to provide their Gross Salary and Deductions (80C, 80D, HRA) or to upload their Form 16 PDF to get a comprehensive Old vs New regime tax comparison.
If they DO provide a salary (e.g. "my salary is 15 lakhs"), extract gross_salary as 1500000 and any other deductions, and set hasFinancialData to true.`;

    const extractedData = await structuredLlm.invoke([
      new SystemMessage(systemPrompt),
      new HumanMessage(content),
    ]);

    if (!extractedData.hasFinancialData || !extractedData.gross_salary) {
      return NextResponse.json({
        success: true,
        message: extractedData.conversationalReply || "Hello! I am The Tax Auditor. Please provide your annual gross salary, or upload a Form 16 PDF so I can compute your tax breakdown!",
      });
    }

    // Hit the exact python math endpoint safely using the Groq Extracted Integers natively!
    const backendUrl = "http://127.0.0.1:8000/api/tax-wizard/manual";
    
    const backendResponse = await fetch(backendUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
         gross_salary: extractedData.gross_salary || 0,
         hra_received: extractedData.hra_received || 0,
         deduction_80c: extractedData.deduction_80c || 0,
         deduction_80d: extractedData.deduction_80d || 0
      }),
    });

    if (!backendResponse.ok) {
      return NextResponse.json(
        { message: "Python Auditor mathematical engine error." },
        { status: backendResponse.status }
      );
    }

    const data = await backendResponse.json();
    const comparison = data.tax_comparison;
    
    const msg = `### 🧑‍⚖️ Live Groq Tax Analysis Complete
    
I have dynamically parsed your input of **₹${extractedData.gross_salary.toLocaleString('en-IN')}** perfectly using native ChatGroq extraction! Based on the true mathematical calculation from Python:

*   **Old Regime Tax Liability**: ₹${comparison.old_regime.total_tax_payable.toLocaleString('en-IN')}
*   **New Regime Tax Liability**: ₹${comparison.new_regime.total_tax_payable.toLocaleString('en-IN')}

**Verdict:** ${comparison.recommendation_reason} 

By formally selecting the **${comparison.recommended_regime.toUpperCase()}** regime, you will actively save **₹${comparison.savings_with_recommended.toLocaleString('en-IN')}** in tax capital this financial year.`;

    return NextResponse.json({
      success: true,
      message: msg,
    });
  } catch (error) {
    console.error("Auditor Route Dynamic Chat Error:", error);
    return NextResponse.json(
      { message: "Could not stream the Groq pipeline to the Auditor API." },
      { status: 500 }
    );
  }
}
