import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth/next";
import { authOptions } from "../auth/[...nextauth]/route";
import { prisma } from "@/lib/prisma";

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Fetch all chat sessions for the user
    const chatSessions = await prisma.chatSession.findMany({
      where: { userId: session.user.id },
      include: {
        messages: {
          orderBy: { timestamp: "asc" },
        },
      },
      orderBy: { updatedAt: "desc" },
    });

    return NextResponse.json({ sessions: chatSessions });
  } catch (error) {
    console.error("Error fetching sessions:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const { id, title, activeAgent, messages } = body;

    // Create or update the chat session
    const chatSession = await prisma.chatSession.upsert({
      where: { id: id || "" },
      update: {
        title,
        activeAgent,
        // Since sqlite/prisma relations can be complex to deeply update, 
        // a simple approach is deleting existing messages and inserting new ones for this prototype,
        // or just rely on appending in a separate route. Here we'll manage messages by ID.
      },
      create: {
        id,
        userId: session.user.id,
        title: title || "New Chat",
        activeAgent: activeAgent || "manager",
      },
    });

    // Handle messages sync: In this pattern, we just iterate and upsert them
    if (messages && messages.length > 0) {
      for (const msg of messages) {
        await prisma.message.upsert({
          where: { id: msg.id || "" },
          update: {
            content: msg.content,
            role: msg.role,
            agentId: msg.agentId,
          },
          create: {
            id: msg.id,
            chatSessionId: chatSession.id,
            role: msg.role,
            content: msg.content,
            agentId: msg.agentId,
            timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date(),
          },
        });
      }
    }

    return NextResponse.json({ session: chatSession });
  } catch (error) {
    console.error("Error saving session:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}
