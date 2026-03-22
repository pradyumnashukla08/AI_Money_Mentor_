"use client";
import React, { useRef, useEffect } from "react";
import { useChat } from "@/context/ChatContext";
import { getAgent } from "@/lib/agentConfig";
import MessageBubble from "./MessageBubble";
import ChatInput from "./ChatInput";
import WelcomeScreen from "./WelcomeScreen";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";

export default function ChatInterface() {
  const { messages, isLoading, activeAgent } = useChat();
  const chatEndRef = useRef<HTMLDivElement>(null);
  const agent = getAgent(activeAgent);
  const { status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login");
    }
  }, [status, router]);

  // Auto-scroll to latest message
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="main-content">
      {messages.length === 0 ? (
        <>
          <WelcomeScreen />
          <ChatInput />
        </>
      ) : (
        <>
          <div className="chat-area" id="chat-area">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}

            {/* Typing indicator */}
            {isLoading && (
              <div className="typing-indicator">
                <div
                  className="message-avatar"
                  style={{ background: `${agent.color}22` }}
                >
                  {agent.icon}
                </div>
                <div className="typing-dots">
                  <div
                    className="typing-dot"
                    style={{ background: agent.color }}
                  />
                  <div
                    className="typing-dot"
                    style={{ background: agent.color }}
                  />
                  <div
                    className="typing-dot"
                    style={{ background: agent.color }}
                  />
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>
          <ChatInput />
        </>
      )}
    </div>
  );
}
