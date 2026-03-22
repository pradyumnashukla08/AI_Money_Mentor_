'use client';
import React from 'react';
import { ChatProvider } from '@/context/ChatContext';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import ChatInterface from '@/components/ChatInterface';

export default function Home() {
  return (
    <ChatProvider>
      <div className="app-shell">
        <Header />
        <Sidebar />
        <ChatInterface />
      </div>
    </ChatProvider>
  );
}
