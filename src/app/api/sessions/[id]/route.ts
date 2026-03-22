import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth/next";
import { authOptions } from "../../auth/[...nextauth]/route";
import { prisma } from "@/lib/prisma";

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> } // In Next.js 15 App router, params is implicitly a Promise in modern async route handlers
) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { id } = await params;
    
    // First, verify the session belongs to the user
    const targetSession = await prisma.chatSession.findUnique({
      where: { id },
    });

    if (!targetSession) {
      return NextResponse.json({ error: "Session not found" }, { status: 404 });
    }

    if (targetSession.userId !== session.user.id) {
      return NextResponse.json({ error: "Forbidden" }, { status: 403 });
    }

    // Since message deletion cascades usually, or to be safe we can manually delete linked messages
    await prisma.message.deleteMany({
      where: { chatSessionId: id },
    });

    // Delete the session root
    await prisma.chatSession.delete({
      where: { id },
    });

    return NextResponse.json({ success: true, message: "Session deleted" });
  } catch (error) {
    console.error("Error deleting session:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}
