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

    const { searchParams } = new URL(request.url);
    const topic = searchParams.get("topic");

    const memories = await prisma.agentMemory.findMany({
      where: {
        userId: session.user.id,
        ...(topic && { topic }),
      },
      orderBy: { updatedAt: "desc" },
    });

    return NextResponse.json({ memories });
  } catch (error) {
    console.error("Error fetching agent memory:", error);
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
    const { topic, memoryData } = body;

    if (!topic || !memoryData) {
      return NextResponse.json({ error: "Topic and memoryData are required" }, { status: 400 });
    }

    // Upsert memory by topic
    // First try to find existing memory by topic to update, otherwise create new
    const existingMemory = await prisma.agentMemory.findFirst({
      where: {
        userId: session.user.id,
        topic: topic,
      },
    });

    let savedMemory;
    if (existingMemory) {
      savedMemory = await prisma.agentMemory.update({
        where: { id: existingMemory.id },
        data: { memoryData },
      });
    } else {
      savedMemory = await prisma.agentMemory.create({
        data: {
          userId: session.user.id,
          topic,
          memoryData,
        },
      });
    }

    return NextResponse.json({ memory: savedMemory }, { status: 201 });
  } catch (error) {
    console.error("Error saving agent memory:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}
