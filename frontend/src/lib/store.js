import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { generateMockResponse } from './mockNLP';

const useJarvisStore = create(
  persist(
    (set, get) => ({
      // UI State
      sidebarOpen: true,
      currentThreadId: null,
      isStreaming: false,
      isRecording: false,
      showSettings: false,

      // Threads Management
      threads: [],
      currentMessages: [],

      // Settings
      settings: {
        model: 'gpt-4',
        temperature: 0.7,
        topP: 0.9,
        voiceEnabled: true,
        language: 'fr-FR',
        performanceMode: false,
        reducedMotion: false,
      },

      // Models Configuration
      availableModels: [
        { id: 'gpt-4', name: 'GPT-4', provider: 'openai', description: 'Most capable model' },
        { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', provider: 'openai', description: 'Fast and efficient' },
        { id: 'claude-3-opus', name: 'Claude 3 Opus', provider: 'anthropic', description: 'Advanced reasoning' },
        { id: 'claude-3-sonnet', name: 'Claude 3 Sonnet', provider: 'anthropic', description: 'Balanced performance' },
        { id: 'gemini-pro', name: 'Gemini Pro', provider: 'google', description: 'Google\'s flagship model' },
        { id: 'mistral-large', name: 'Mistral Large', provider: 'mistral', description: 'European AI excellence' },
        { id: 'llama-2-70b', name: 'Llama 2 70B', provider: 'ollama', description: 'Open source model' },
      ],

      // Actions
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      
      setCurrentThread: (threadId) => {
        const threads = get().threads;
        const thread = threads.find(t => t.id === threadId);
        set({ 
          currentThreadId: threadId,
          currentMessages: thread ? thread.messages : []
        });
      },

      createNewThread: () => {
        const newThread = {
          id: `thread-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          title: 'Nouvelle conversation',
          model: get().settings.model,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          messages: []
        };
        
        set(state => ({
          threads: [newThread, ...state.threads],
          currentThreadId: newThread.id,
          currentMessages: []
        }));
        
        return newThread.id;
      },

      updateThreadTitle: (threadId, title) => {
        set(state => ({
          threads: state.threads.map(t => 
            t.id === threadId 
              ? { ...t, title, updatedAt: new Date().toISOString() }
              : t
          )
        }));
      },

      deleteThread: (threadId) => {
        set(state => {
          const newThreads = state.threads.filter(t => t.id !== threadId);
          const isCurrentThread = state.currentThreadId === threadId;
          
          return {
            threads: newThreads,
            currentThreadId: isCurrentThread ? null : state.currentThreadId,
            currentMessages: isCurrentThread ? [] : state.currentMessages
          };
        });
      },

      addMessage: (message) => {
        const threadId = get().currentThreadId;
        if (!threadId) return;

        const newMessage = {
          id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          timestamp: new Date().toISOString(),
          ...message
        };

        set(state => ({
          currentMessages: [...state.currentMessages, newMessage],
          threads: state.threads.map(t => 
            t.id === threadId 
              ? { 
                  ...t, 
                  messages: [...(t.messages || []), newMessage],
                  updatedAt: new Date().toISOString(),
                  title: t.messages.length === 0 ? message.content.slice(0, 50) + '...' : t.title
                }
              : t
          )
        }));
      },

      updateMessage: (messageId, updates) => {
        const threadId = get().currentThreadId;
        if (!threadId) return;

        set(state => ({
          currentMessages: state.currentMessages.map(m => 
            m.id === messageId ? { ...m, ...updates } : m
          ),
          threads: state.threads.map(t => 
            t.id === threadId 
              ? {
                  ...t,
                  messages: t.messages.map(m => 
                    m.id === messageId ? { ...m, ...updates } : m
                  ),
                  updatedAt: new Date().toISOString()
                }
              : t
          )
        }));
      },

      // Chat Actions
      sendMessage: async (content) => {
        const { addMessage, settings, currentThreadId } = get();
        
        if (!currentThreadId) {
          get().createNewThread();
        }

        // Add user message
        addMessage({
          role: 'user',
          content,
          model: settings.model
        });

        // Set streaming state
        set({ isStreaming: true });

        // Add assistant message placeholder
        const assistantMessage = {
          role: 'assistant',
          content: '',
          model: settings.model,
          streaming: true
        };
        
        addMessage(assistantMessage);
        const messageId = assistantMessage.id;

        // Simulate streaming response
        try {
          const response = await generateMockResponse(content, settings);
          
          // Stream the response character by character
          for (let i = 0; i <= response.length; i++) {
            await new Promise(resolve => setTimeout(resolve, 30 + Math.random() * 20));
            
            get().updateMessage(messageId, {
              content: response.slice(0, i),
              streaming: i < response.length
            });
          }
        } catch (error) {
          get().updateMessage(messageId, {
            content: 'Erreur lors de la génération de la réponse.',
            streaming: false,
            error: true
          });
        } finally {
          set({ isStreaming: false });
        }
      },

      // Voice Actions
      startRecording: () => set({ isRecording: true }),
      stopRecording: () => {
        set({ isRecording: false });
        // Mock transcription
        setTimeout(() => {
          // This would be replaced with actual STT result
          console.log('Mock transcription completed');
        }, 500);
      },

      // Settings Actions
      updateSettings: (updates) => set(state => ({
        settings: { ...state.settings, ...updates }
      })),

      toggleSettings: () => set(state => ({ showSettings: !state.showSettings })),

      // Export/Import
      exportData: () => {
        const { threads, settings } = get();
        return {
          version: '1.0',
          exportDate: new Date().toISOString(),
          threads,
          settings
        };
      },

      importData: (data) => {
        if (data.version === '1.0') {
          set({
            threads: data.threads || [],
            settings: { ...get().settings, ...data.settings }
          });
        }
      },

      // Clear all data
      clearAllData: () => set({
        threads: [],
        currentThreadId: null,
        currentMessages: []
      })
    }),
    {
      name: 'jarvis-storage',
      partialize: (state) => ({
        threads: state.threads,
        settings: state.settings,
        currentThreadId: state.currentThreadId
      })
    }
  )
);

export default useJarvisStore;