'use client';

import { useState, useEffect, useCallback } from 'react';
import { PaperAirplaneIcon } from '@heroicons/react/24/solid';
import ChatMessage from './components/ChatMessage';
import ModelSelector from './components/ModelSelector';
import Settings from './components/Settings';
import ConversationList from './components/ConversationList';
// Types removed for JSX compatibility
import ThemeToggle from "./components/ThemeToggle";

// Configuration pour Jarvis - Utilise le backend API (qui gère Ollama + MCP + DB)
const getSavedUrl = () => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('backendUrl') || 'http://localhost:8000';
  }
  return 'http://localhost:8000';
};

// 生成唯一ID
const generateId = () => Math.random().toString(36).substring(2) + Date.now().toString(36);

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('');
  const [baseUrl, setBaseUrl] = useState(getSavedUrl);
  const [error, setError] = useState(null);
  const [streamingMessage, setStreamingMessage] = useState('');

  // 初始化加载
  useEffect(() => {
    setMounted(true);
    const savedConversations = localStorage.getItem('conversations');
    if (savedConversations) {
      try {
        const parsed = JSON.parse(savedConversations);
        setConversations(parsed);
        if (parsed.length > 0) {
          setCurrentConversationId(parsed[0].id);
        }
      } catch (e) {
        console.error('Failed to parse saved conversations:', e);
      }
    }
  }, []);

  // 保存会话到localStorage
  useEffect(() => {
    if (mounted) {
      localStorage.setItem('conversations', JSON.stringify(conversations));
    }
  }, [conversations, mounted]);

  const currentConversation = conversations.find(c => c.id === currentConversationId);

  const handleNewConversation = useCallback(() => {
    const newConversation = {
      id: generateId(),
      title: 'New Chat',
      messages: [],
      model: selectedModel,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    setConversations(prev => [newConversation, ...prev]);
    setCurrentConversationId(newConversation.id);
  }, [selectedModel]);

  const handleDeleteConversation = useCallback((id: string) => {
    setConversations(prev => prev.filter(c => c.id !== id));
    if (currentConversationId === id) {
      const remaining = conversations.filter(c => c.id !== id);
      setCurrentConversationId(remaining.length > 0 ? remaining[0]?.id || null : null);
    }
  }, [currentConversationId, conversations]);

  const handleUrlChange = useCallback((newUrl: string) => {
    setBaseUrl(newUrl);
    localStorage.setItem('ollamaUrl', newUrl);
  }, []);

  const updateConversationTitle = useCallback((id: string, firstMessage: string) => {
    setConversations(prev => prev.map(conv => {
      if (conv.id === id) {
        return {
          ...conv,
          title: firstMessage.substring(0, 30) + (firstMessage.length > 30 ? '...' : ''),
          updatedAt: new Date().toISOString()
        };
      }
      return conv;
    }));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || !selectedModel || loading) return;

    if (!currentConversationId) {
      handleNewConversation();
      return;
    }

    const newMessage = { role: 'user', content: input };
    
    setConversations(prev => prev.map(conv => {
      if (conv.id === currentConversationId) {
        const updatedMessages = [...conv.messages, newMessage];
        if (conv.messages.length === 0) {
          updateConversationTitle(conv.id, input);
        }
        return {
          ...conv,
          messages: updatedMessages,
          updatedAt: new Date().toISOString()
        };
      }
      return conv;
    }));

    setInput('');
    setLoading(true);
    setError(null);
    setStreamingMessage('');

    try {
      const response = await fetch(`${baseUrl}/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          user_id: 'frontend_user'
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      const assistantMessage = data.response;

      if (assistantMessage) {
        setConversations(prev => prev.map(conv => {
          if (conv.id === currentConversationId) {
            return {
              ...conv,
              messages: [...conv.messages, { role: 'assistant', content: assistantMessage }],
              updatedAt: new Date().toISOString()
            };
          }
          return conv;
        }));
      }
    } catch (error) {
      console.error('Error in chat request:', error);
      setError(error instanceof Error ? error.message : 'Failed to send message');
    } finally {
      setLoading(false);
      setStreamingMessage('');
    }
  };

  const displayMessages = currentConversation ? [
    ...currentConversation.messages,
    ...(streamingMessage ? [{ role: 'assistant', content: streamingMessage }] : [])
  ] : [];

  const handleImportConversations = useCallback((imported) => {
    setConversations(prev => {
      const existingIds = new Set(prev.map(c => c.id));
      const newConversations = imported.filter(c => !existingIds.has(c.id));
      return [...newConversations, ...prev];
    });
  }, []);

  if (!mounted) {
    return null;
  }

  return (
    <div className="flex h-screen">
      <ConversationList
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSelect={(conv) => setCurrentConversationId(conv.id)}
        onNew={handleNewConversation}
        onDelete={handleDeleteConversation}
      />
      
      <div className="flex-1 flex flex-col">
        <header className="p-4 border-b">
          <div className="flex items-center justify-between max-w-7xl mx-auto w-full">
            <h1 className="text-2xl font-bold">Ollama Chat</h1>
            <div className="flex items-center gap-4">
              <ModelSelector
                selectedModel={selectedModel}
                onModelSelect={setSelectedModel}
                baseUrl={baseUrl}
              />
              <Settings 
                onUrlChange={handleUrlChange} 
                initialUrl={baseUrl}
                conversations={conversations}
                onConversationsImport={handleImportConversations}
              />
              <ThemeToggle />
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-auto p-4">
          <div className="max-w-6xl mx-auto">
            {displayMessages.map((message, index) => (
              <ChatMessage
                key={`${currentConversationId}-${index}`}
                role={message.role}
                content={message.content}
              />
            ))}
            {error && (
              <div className="text-error text-center p-4">
                Error: {error}
              </div>
            )}
          </div>
        </main>

        <footer className="p-4 border-t">
          <form onSubmit={handleSubmit} className="max-w-4xl mx-auto flex gap-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="input input-bordered flex-1"
              disabled={loading || !selectedModel}
            />
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !selectedModel || !input.trim()}
            >
              <PaperAirplaneIcon className="w-5 h-5" />
            </button>
          </form>
        </footer>
      </div>
    </div>
  );
}