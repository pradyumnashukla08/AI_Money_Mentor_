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

    let profile = await prisma.financialProfile.findUnique({
      where: { userId: session.user.id },
    });

    if (!profile) {
      // Create default profile if it doesn't exist
      profile = await prisma.financialProfile.create({
        data: {
          userId: session.user.id,
        },
      });
    }

    return NextResponse.json({ profile });
  } catch (error) {
    console.error("Error fetching financial profile:", error);
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
    const { monthlyIncome, totalAssets, riskTolerance, goals } = body;

    const profile = await prisma.financialProfile.upsert({
      where: { userId: session.user.id },
      update: {
        monthlyIncome: Number(monthlyIncome) || 0,
        totalAssets: Number(totalAssets) || 0,
        riskTolerance: riskTolerance || "moderate",
        goals: goals || "",
      },
      create: {
        userId: session.user.id,
        monthlyIncome: Number(monthlyIncome) || 0,
        totalAssets: Number(totalAssets) || 0,
        riskTolerance: riskTolerance || "moderate",
        goals: goals || "",
      },
    });

    return NextResponse.json({ profile }, { status: 200 });
  } catch (error) {
    console.error("Error updating financial profile:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}
