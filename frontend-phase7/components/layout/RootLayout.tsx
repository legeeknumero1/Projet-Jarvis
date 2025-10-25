/**
 * Layout racine de l'application
 */

import React from 'react';
import { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '@/styles/globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Jarvis AI Assistant',
  description: 'Assistant IA intelligent et résilient',
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
};

interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <head>
        <meta charSet="utf-8" />
        <meta name="theme-color" content="#000000" />
      </head>
      <body className={inter.className}>
        <div className="flex h-screen flex-col">
          {children}
        </div>
      </body>
    </html>
  );
}
