'use client';
import React, { createContext, useContext, useState, useCallback, ReactNode, useEffect } from 'react';
import { useSession } from "next-auth/react";
import { Message, AgentId, ChatSession, RouteResult } from '@/lib/types';
import { routeFileUpload } from '@/lib/agentRouter';
import { getAgent } from '@/lib/agentConfig';

interface ChatContextType {
  messages: Message[];
  activeAgent: AgentId;
  isLoading: boolean;
  sessions: ChatSession[];
  routeInfo: RouteResult | null;
  sidebarOpen: boolean;
  activeSessionId: string | null;
  sendMessage: (content: string) => void;
  handleFileUpload: (file: File) => void;
  setActiveAgent: (agent: AgentId) => void;
  clearChat: (agentId?: AgentId) => void;
  loadSession: (sessionId: string) => void;
  deleteSession: (sessionId: string) => Promise<void>;
  toggleSidebar: () => void;
  hasUnreadNotifications: boolean;
  markNotificationsAsRead: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 9);
}

export function ChatProvider({ children }: { children: ReactNode }) {
  const { data: session } = useSession();
  const [messages, setMessages] = useState<Message[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [activeAgent, setActiveAgentState] = useState<AgentId>('manager');
  const [isLoading, setIsLoading] = useState(false);
  const [routeInfo, setRouteInfo] = useState<RouteResult | null>(null);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [hasUnreadNotifications, setHasUnreadNotifications] = useState(false);

  // Fetch past sessions and notifications when logged in
  useEffect(() => {
    if (session?.user) {
      fetch('/api/sessions')
        .then(res => res.json())
        .then(data => {
          if (data.sessions) {
            setSessions(data.sessions);
          }
        })
        .catch(console.error);
        
      fetch('/api/notifications')
        .then(res => res.json())
        .then(data => {
          if (data.notifications) {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            setHasUnreadNotifications(data.notifications.some((n: any) => !n.isRead));
          }
        })
        .catch(console.error);
    } else {
      setTimeout(() => {
        setSessions([]);
        setMessages([]);
        setActiveSessionId(null);
        setHasUnreadNotifications(false);
      }, 0);
    }
  }, [session]);

  const markNotificationsAsRead = useCallback(() => {
    setHasUnreadNotifications(false);
  }, []);

  const saveCurrentSession = useCallback(async (updatedMessages: Message[], sessionId: string) => {
    if (!session?.user) return;
    
    try {
      await fetch('/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: sessionId,
          title: updatedMessages.length > 0 ? updatedMessages[0].content.slice(0, 40) : "New Chat",
          activeAgent,
          messages: updatedMessages
        })
      });
      // Refresh sidebar list
      const res = await fetch('/api/sessions');
      const data = await res.json();
      if (data.sessions) setSessions(data.sessions);
    } catch (err) {
      console.error("Failed to save session", err);
    }
  }, [activeAgent, session]);

  const loadSession = useCallback((sessionId: string) => {
    const target = sessions.find(s => s.id === sessionId);
    if (target) {
      setActiveSessionId(target.id);
      setActiveAgentState(target.activeAgent as AgentId || 'manager');
      setMessages(target.messages || []);
      setRouteInfo(null);
    }
  }, [sessions]);

  const deleteSession = useCallback(async (sessionId: string) => {
    if (!session?.user) return;
    
    // optimistic UI update
    setSessions((prev) => prev.filter(s => s.id !== sessionId));
    if (activeSessionId === sessionId) {
      setMessages([]);
      setActiveSessionId(null);
    }

    try {
      await fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' });
    } catch (err) {
      console.error("Failed to delete session", err);
      // fallback refresh
      const res = await fetch('/api/sessions');
      const data = await res.json();
      if (data.sessions) setSessions(data.sessions);
    }
  }, [session, activeSessionId]);

  const sendMessage = useCallback(
    (content: string) => {
      const currentSessionId = activeSessionId || generateId();
      if (!activeSessionId) setActiveSessionId(currentSessionId);

      const userMsg: Message = {
        id: generateId(),
        role: 'user',
        content,
        agentId: activeAgent,
        timestamp: new Date(),
      };

      const updatedMessages = [...messages, userMsg];
      setMessages(updatedMessages);
      setIsLoading(true);

      if (session?.user) saveCurrentSession(updatedMessages, currentSessionId);

      const endpoint = getAgent(activeAgent).endpoint;

      fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: updatedMessages,
          currentAgent: activeAgent,
          hasFile: false,
        }),
      })
        .then((res) => res.json())
        .then(async (data) => {
          if (data.routing) {
            setRouteInfo(data.routing);
            if (data.routing.agent !== activeAgent && data.routing.confidence > 0.3) {
              const newAgentId = data.routing.agent;
              setActiveAgentState(newAgentId);
              
              // Add the transition message from orchestrator
              const transitionMsg: Message = {
                id: generateId(),
                role: 'agent',
                content: data.message || `Handing off to ${getAgent(newAgentId).name}...`,
                agentId: activeAgent,
                timestamp: new Date(),
                routingInfo: data.routing,
              };
              
              setMessages((m) => {
                const transitionState = [...m, transitionMsg];
                if (session?.user) saveCurrentSession(transitionState, currentSessionId);
                return transitionState;
              });

              if (newAgentId !== 'manager') {
                // Forward immediately to the specialized Python Agent Proxy
                try {
                  const nextEndpoint = getAgent(newAgentId).endpoint;
                  const resSpecialist = await fetch(nextEndpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ messages: updatedMessages, currentAgent: newAgentId }),
                  });
                  const specData = await resSpecialist.json();

                  const specialistMsg: Message = {
                    id: generateId(),
                    role: 'agent',
                    content: specData.error || specData.message || "I am ready.",
                    agentId: newAgentId,
                    timestamp: new Date(),
                  };
                  
                  setMessages((m) => {
                    const finalState = [...m, specialistMsg];
                    if (session?.user) saveCurrentSession(finalState, currentSessionId);
                    return finalState;
                  });
                } catch (err) {
                   console.error("Handoff failed", err);
                } finally {
                   setIsLoading(false);
                }
                
                return; // prevent the normal trailing logic
              }
            }
          }

          const agentMsg: Message = {
            id: generateId(),
            role: 'agent',
            content: data.error || data.message || "Sorry, I couldn't process that request.",
            agentId: data.routing?.agent || activeAgent,
            timestamp: new Date(),
            routingInfo: data.routing,
          };
          setMessages((m) => {
            const newMsgs = [...m, agentMsg];
            if (session?.user) saveCurrentSession(newMsgs, currentSessionId);
            return newMsgs;
          });
          setIsLoading(false);
        })
        .catch((error) => {
          console.error('Chat error:', error);
          setIsLoading(false);
        });
    },
    [messages, activeAgent, activeSessionId, session, saveCurrentSession]
  );

  const handleFileUpload = useCallback(
    (file: File) => {
      const currentSessionId = activeSessionId || generateId();
      if (!activeSessionId) setActiveSessionId(currentSessionId);

      const route = routeFileUpload(file.name, file.type);
      setRouteInfo(route);
      setActiveAgentState(route.agent);

      const userMsg: Message = {
        id: generateId(),
        role: 'user',
        content: `📎 Uploaded Document: **${file.name}** (${(file.size / 1024).toFixed(1)} KB)`,
        agentId: activeAgent,
        timestamp: new Date(),
        attachments: [{ name: file.name, type: file.type, size: file.size }],
      };

      const updatedMessages = [...messages, userMsg];
      setMessages(updatedMessages);
      setIsLoading(true);

      if (session?.user) saveCurrentSession(updatedMessages, currentSessionId);

      // Create FormData implicitly matching Python FastAPI schema: `file: UploadFile = File(...)`
      const formData = new FormData();
      formData.append("file", file);

      // Send the binary data to the local Next.js Edge proxy, bypassing all Device IPs / CORS logic
      fetch('/api/tax-upload', {
        method: 'POST',
        // DO NOT set Content-Type header manually when using FormData. The browser sets the boundary automatically.
        body: formData,
      })
        .then((res) => {
          if (!res.ok) throw new Error("Python Pipeline Rejected Document");
          return res.json();
        })
        .then((data) => {
          const comparison = data.tax_comparison;
          
          let breakdownText = `### 🧑‍⚖️ Form 16 Tax Wizard Complete\n\nI have actively ingested and parsed your uploaded PDF **${file.name}**.\n\n`;
          
          if (comparison && comparison.old_regime) {
             breakdownText += `*   **Old Regime Tax Liability**: ₹${comparison.old_regime.total_tax_payable.toLocaleString('en-IN')}\n`;
             breakdownText += `*   **New Regime Tax Liability**: ₹${comparison.new_regime.total_tax_payable.toLocaleString('en-IN')}\n\n`;
             breakdownText += `**Verdict:** ${comparison.recommendation_reason}\n\n`;
             breakdownText += `By electing the **${comparison.recommended_regime.toUpperCase()}** framework, you will structurally save **₹${comparison.savings_with_recommended.toLocaleString('en-IN')}**.`;
          } else {
             breakdownText += `Extracted Data: \n\`\`\`json\n${JSON.stringify(data.extracted_data || data, null, 2)}\n\`\`\``;
          }

          const agentMsg: Message = {
            id: generateId(),
            role: 'agent',
            content: breakdownText,
            agentId: 'auditor',
            timestamp: new Date(),
            routingInfo: route,
          };
          setMessages((m) => {
            const newMsgs = [...m, agentMsg];
            if (session?.user) saveCurrentSession(newMsgs, currentSessionId);
            return newMsgs;
          });
        })
        .catch((error) => {
          console.error("PDF Parsing Failed:", error);
          const agentMsg: Message = {
            id: generateId(),
            role: 'agent',
            content: "⚠️ I could not parse your document format. Ensure the Python backend is currently running and it is a valid readable PDF.",
            agentId: 'auditor',
            timestamp: new Date(),
            routingInfo: route,
          };
          setMessages((m) => {
            const newMsgs = [...m, agentMsg];
            if (session?.user) saveCurrentSession(newMsgs, currentSessionId);
            return newMsgs;
          });
        })
        .finally(() => setIsLoading(false));
    },
    [messages, activeAgent, activeSessionId, session, saveCurrentSession]
  );

  const setActiveAgent = useCallback((agent: AgentId) => {
    setActiveAgentState(agent);
  }, []);

  const clearChat = useCallback((agentId?: AgentId) => {
    setMessages([]);
    setRouteInfo(null);
    setActiveAgentState(agentId || 'manager');
    setActiveSessionId(null);
  }, []);

  const toggleSidebar = useCallback(() => {
    setSidebarOpen((prev) => !prev);
  }, []);

  return (
    <ChatContext.Provider
      value={{
        messages,
        activeAgent,
        isLoading,
        sessions,
        routeInfo,
        sidebarOpen,
        activeSessionId,
        sendMessage,
        handleFileUpload,
        setActiveAgent,
        clearChat,
        loadSession,
        deleteSession,
        toggleSidebar,
        hasUnreadNotifications,
        markNotificationsAsRead,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChat(): ChatContextType {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
}
