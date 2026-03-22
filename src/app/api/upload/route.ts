import { NextRequest, NextResponse } from 'next/server';
import { routeFileUpload } from '@/lib/agentRouter';
import { AGENTS } from '@/lib/agentConfig';
import { getServerSession } from "next-auth/next";
import { authOptions } from "../auth/[...nextauth]/route";
import { prisma } from "@/lib/prisma";

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const formData = await request.formData();
    const file = formData.get('file') as File | null;

    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      );
    }

    // Save document metadata in database
    const document = await prisma.document.create({
      data: {
        userId: session.user.id,
        name: file.name,
        type: file.type,
        size: file.size,
        url: `/uploads/mock-path/${file.name}`, // In production: S3 or cloud storage URL
      }
    });

    // Route based on file type
    const routeResult = routeFileUpload(file.name, file.type);
    const targetAgent = AGENTS[routeResult.agent];

    return NextResponse.json({
      success: true,
      file: {
        id: document.id,
        name: document.name,
        type: document.type,
        size: document.size,
      },
      routing: {
        agent: routeResult.agent,
        agentName: targetAgent.name,
        agentTitle: targetAgent.title,
        confidence: routeResult.confidence,
        reasoning: routeResult.reasoning,
      },
      message: `${targetAgent.name} has received your file "${document.name}" and is ready to process it.`,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Upload API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
