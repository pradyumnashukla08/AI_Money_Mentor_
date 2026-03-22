'use client';
import React from 'react';
import { useChat } from '@/context/ChatContext';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useSession } from 'next-auth/react';
import Image from 'next/image';

export default function Header() {
  const { toggleSidebar, hasUnreadNotifications } = useChat();
  const pathname = usePathname();
  const { data: session } = useSession();

  return (
    <header className="header">
      <div className="header-left">
        <button
          className="header-toggle"
          onClick={toggleSidebar}
          aria-label="Toggle sidebar"
          id="sidebar-toggle"
        >
          ☰
        </button>
        <Link href="/" className="header-brand" style={{ textDecoration: 'none' }}>
          <span className="header-logo">AI Money Mentor</span>
          <span className="header-et">Powered by ET</span>
        </Link>
      </div>

      <div className="header-right">
        <Link href="/" style={{ textDecoration: 'none' }}>
          <button className="header-btn" aria-label="Chat" id="chat-nav-btn" style={{ background: pathname === '/' ? 'var(--surface-highest)' : '' }}>
            💬
          </button>
        </Link>
        <Link href="/search" style={{ textDecoration: 'none' }}>
          <button className="header-btn" aria-label="Search" id="search-btn" title="Search" style={{ background: pathname === '/search' ? 'var(--surface-highest)' : '' }}>
            🔍
          </button>
        </Link>
        <Link href="/notifications" style={{ textDecoration: 'none' }}>
          <button className="header-btn" aria-label="Notifications" id="notification-btn" style={{ background: pathname === '/notifications' ? 'var(--surface-highest)' : '' }}>
            🔔
            {hasUnreadNotifications && <span className="notification-dot" />}
          </button>
        </Link>
        <Link href="/profile" style={{ textDecoration: 'none' }}>
          <div className="header-avatar" id="user-avatar" title="User Profile" style={{ 
            boxShadow: pathname === '/profile' ? 'var(--shadow-glow-gold)' : '',
            position: 'relative',
            overflow: 'hidden'
          }}>
            {session?.user ? (
              <Image 
                src={session.user.image || `https://ui-avatars.com/api/?name=${encodeURIComponent(session.user.name || session.user.email || 'User')}&background=F0B90B&color=000`}
                alt="Profile"
                fill
                style={{ objectFit: 'cover' }}
                sizes="40px"
              />
            ) : (
              "P"
            )}
          </div>
        </Link>
      </div>
    </header>
  );
}
