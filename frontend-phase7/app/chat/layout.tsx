/**
 * Layout pour la section chat
 */

'use client';

import React, { useState } from 'react';
import { Header } from '@/components/layout/Header';
import { Sidebar } from '@/components/layout/Sidebar';

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-background">
      {/* En-tête */}
      <Header onMenuClick={() => setIsSidebarOpen(!isSidebarOpen)} />

      {/* Contenu principal */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar mobile overlay */}
        {isSidebarOpen && (
          <div
            className="fixed inset-0 z-40 bg-black/50 lg:hidden"
            onClick={() => setIsSidebarOpen(false)}
          />
        )}

        {/* Sidebar */}
        <div
          className={`fixed inset-y-0 left-0 z-50 lg:static lg:z-0 transition-all duration-300 ${
            isSidebarOpen ? 'w-64' : '-translate-x-full lg:translate-x-0'
          }`}
        >
          <Sidebar
            isOpen={isSidebarOpen}
            onClose={() => setIsSidebarOpen(false)}
          />
        </div>

        {/* Contenu */}
        <div className="flex-1 overflow-hidden">
          {children}
        </div>
      </div>
    </div>
  );
}
