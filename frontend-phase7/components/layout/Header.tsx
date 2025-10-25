/**
 * En-tête de navigation
 */

'use client';

import React from 'react';
import Link from 'next/link';
import { useUserStore } from '@/store';
import { Menu, LogOut, Settings } from 'lucide-react';

interface HeaderProps {
  onMenuClick?: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  const { user, logout } = useUserStore();

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  return (
    <header className="border-b border-border bg-card">
      <div className="flex items-center justify-between px-4 py-3 sm:px-6">
        {/* Logo & Titre */}
        <div className="flex items-center gap-4">
          <button
            onClick={onMenuClick}
            className="rounded-lg p-2 hover:bg-muted lg:hidden"
            aria-label="Menu"
          >
            <Menu className="h-5 w-5" />
          </button>

          <Link href="/" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-primary" />
            <span className="hidden font-semibold sm:inline">Jarvis</span>
          </Link>
        </div>

        {/* Infos utilisateur */}
        <div className="flex items-center gap-4">
          {user ? (
            <>
              <div className="hidden text-sm sm:block">
                <p className="font-medium">{user.name}</p>
                <p className="text-xs text-muted-foreground">{user.email}</p>
              </div>

              <div className="flex items-center gap-2">
                <button
                  className="rounded-lg p-2 hover:bg-muted"
                  aria-label="Paramètres"
                >
                  <Settings className="h-5 w-5" />
                </button>

                <button
                  onClick={handleLogout}
                  className="rounded-lg p-2 hover:bg-destructive hover:text-destructive-foreground"
                  aria-label="Déconnexion"
                >
                  <LogOut className="h-5 w-5" />
                </button>
              </div>
            </>
          ) : (
            <Link href="/login" className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
              Connexion
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
