/**
 * Barre latérale avec liste des conversations
 */

'use client';

import React, { useEffect } from 'react';
import { useChatStore } from '@/store';
import { chatApi } from '@/lib/api';
import { Plus, Trash2, Archive } from 'lucide-react';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export function Sidebar({ isOpen = true, onClose }: SidebarProps) {
  const { conversations, currentConversation, setConversations, setCurrentConversation } = useChatStore();
  const [isLoading, setIsLoading] = React.useState(false);

  /**
   * Charger les conversations
   */
  useEffect(() => {
    const loadConversations = async () => {
      try {
        setIsLoading(true);
        const response = await chatApi.listConversations(1, 50);
        setConversations(response.items || []);
      } catch (error) {
        console.error('Erreur lors du chargement des conversations:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadConversations();
  }, [setConversations]);

  /**
   * Créer une nouvelle conversation
   */
  const handleNewConversation = async () => {
    try {
      const response = await chatApi.createConversation('Nouvelle conversation');
      if (response.data) {
        setCurrentConversation(response.data);
        onClose?.();
      }
    } catch (error) {
      console.error('Erreur lors de la création:', error);
    }
  };

  /**
   * Supprimer une conversation
   */
  const handleDeleteConversation = async (e: React.MouseEvent, conversationId: string) => {
    e.preventDefault();
    e.stopPropagation();

    if (!confirm('Êtes-vous sûr de vouloir supprimer cette conversation ?')) {
      return;
    }

    try {
      await chatApi.deleteConversation(conversationId);
      setConversations(conversations.filter((c) => c.id !== conversationId));
      if (currentConversation?.id === conversationId) {
        setCurrentConversation(null);
      }
    } catch (error) {
      console.error('Erreur lors de la suppression:', error);
    }
  };

  /**
   * Archiver une conversation
   */
  const handleArchiveConversation = async (e: React.MouseEvent, conversationId: string) => {
    e.preventDefault();
    e.stopPropagation();

    try {
      await chatApi.archiveConversation(conversationId);
      setConversations(
        conversations.map((c) =>
          c.id === conversationId ? { ...c, isArchived: true } : c,
        ),
      );
    } catch (error) {
      console.error('Erreur lors de l\'archivage:', error);
    }
  };

  const activeConversations = conversations.filter((c) => !c.isArchived);

  return (
    <aside className={`flex flex-col border-r border-border bg-card transition-all duration-300 ${
      isOpen ? 'w-64' : 'w-0'
    } overflow-hidden lg:w-64 lg:border-r`}>
      {/* En-tête */}
      <div className="border-b border-border p-4">
        <button
          onClick={handleNewConversation}
          disabled={isLoading}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          <Plus className="h-4 w-4" />
          Nouvelle conversation
        </button>
      </div>

      {/* Liste des conversations */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-2">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full border-2 border-primary border-t-transparent h-6 w-6" />
            </div>
          ) : activeConversations.length === 0 ? (
            <p className="text-center text-sm text-muted-foreground py-8">
              Aucune conversation
            </p>
          ) : (
            activeConversations.map((conversation) => (
              <button
                key={conversation.id}
                onClick={() => {
                  setCurrentConversation(conversation);
                  onClose?.();
                }}
                className={`w-full text-left rounded-lg px-3 py-2 text-sm transition-colors ${
                  currentConversation?.id === conversation.id
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-muted'
                } group`}
              >
                <div className="flex items-center justify-between">
                  <span className="truncate">{conversation.title}</span>
                  <div className="flex gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                    <button
                      onClick={(e) => handleArchiveConversation(e, conversation.id)}
                      className="rounded p-1 hover:bg-muted"
                      title="Archiver"
                    >
                      <Archive className="h-3 w-3" />
                    </button>
                    <button
                      onClick={(e) => handleDeleteConversation(e, conversation.id)}
                      className="rounded p-1 hover:bg-destructive"
                      title="Supprimer"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </div>
                </div>
                {conversation.summary && (
                  <p className="mt-1 text-xs opacity-75 line-clamp-2">{conversation.summary}</p>
                )}
              </button>
            ))
          )}
        </div>
      </div>
    </aside>
  );
}
