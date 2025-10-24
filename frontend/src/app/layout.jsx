import React from "react";
import "./globals.css";

// Remplace next/font/local par CSS standard pour Create React App
export default function RootLayout({ children }) {
  return (
    <html lang="fr">
      <head>
        <title>Jarvis AI Assistant</title>
        <meta name="description" content="Interface moderne pour Jarvis AI" />
      </head>
      <body className="font-sans antialiased">
        {children}
      </body>
    </html>
  );
}