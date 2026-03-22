import type { Metadata } from "next";

import "./globals.css";
import { Providers } from "@/components/Providers";

export const metadata: Metadata = {
  title: "AI Money Mentor — Your AI Financial Advisor | Powered by ET",
  description:
    "AI Money Mentor is your personalized AI-powered financial advisor. Get tax optimization, FIRE planning, portfolio analysis, and life event guidance — all in one platform. Powered by Economic Times.",
  keywords: [
    "AI financial advisor",
    "tax optimization India",
    "FIRE planning",
    "mutual fund portfolio analysis",
    "money health score",
    "Economic Times",
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#0f131f" />
      </head>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
