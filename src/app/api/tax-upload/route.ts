import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    // We completely bypass Next.js FormData parsing to preserve Chrome's native boundary tokens.
    const contentType = request.headers.get("content-type");
    
    if (!contentType || !contentType.includes("multipart/form-data")) {
      return NextResponse.json({ error: "Invalid content type. Expected multipart form" }, { status: 400 });
    }

    // Proxy the untouched binary stream straight to Python, preserving all upload signatures natively.
    const backendResponse = await fetch("http://127.0.0.1:8000/api/tax-wizard/upload", {
      method: "POST",
      headers: {
        "Content-Type": contentType,
      },
      body: request.body,
      // @ts-expect-error - Required by Next.js 14/15 to stream raw Request bodies outbound
      duplex: "half",
    });

    const data = await backendResponse.json();
    return NextResponse.json(data, { status: backendResponse.status });
  } catch (error) {
    console.error("LAN Edge Proxy Transfer Exception:", error);
    return NextResponse.json({ error: "Internal Local Network Proxy Error" }, { status: 500 });
  }
}
