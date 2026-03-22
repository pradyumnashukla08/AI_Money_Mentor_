import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const backendUrl = "http://127.0.0.1:8000/analyst/xirr";

    const backendResponse = await fetch(backendUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!backendResponse.ok) {
      const errorData = await backendResponse.json();
      return NextResponse.json(
        { message: errorData.detail || "Python Analyst engine error." },
        { status: backendResponse.status }
      );
    }

    const data = await backendResponse.json();

    return NextResponse.json({
      success: true,
      message: data.message,
    });
  } catch (error) {
    console.error("Analyst Route Error:", error);
    return NextResponse.json(
      { message: "Could not connect to Python Analyst Agent on port 8000." },
      { status: 500 }
    );
  }
}
