import { useState, useCallback } from 'react';
import { Message, OllamaChatRequest, OllamaStreamChunk } from '@/lib/types/ollama';
import { validateOllamaUrl } from '@/lib/validations';

interface UseOllamaChatProps {
  baseUrl: string;
}

interface UseOllamaChatReturn {
  sendMessage: (message: string, model: string, conversationMessages: Message[]) => Promise<void>;
  isLoading: boolean;
  isStreaming: boolean;
  streamingContent: string;
  error: string | null;
  clearError: () => void;
}

export function useOllamaChat({ baseUrl }: UseOllamaChatProps): UseOllamaChatReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [error, setError] = useState<string | null>(null);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const sendMessage = useCallback(async (
    message: string,
    model: string,
    conversationMessages: Message[]
  ) => {
    // Validation de l'URL
    if (!validateOllamaUrl(baseUrl)) {
      setError('Invalid Ollama URL. Please check your configuration.');
      return;
    }

    // Validation du message
    if (!message.trim()) {
      setError('Message cannot be empty.');
      return;
    }

    if (!model.trim()) {
      setError('Model must be selected.');
      return;
    }

    setIsLoading(true);
    setIsStreaming(true);
    setStreamingContent('');
    setError(null);

    try {
      const url = new URL('/api/chat', baseUrl);
      
      const requestBody: OllamaChatRequest = {
        model,
        messages: [...conversationMessages, { role: 'user', content: message }],
        stream: true,
        options: {
          temperature: 0.7,
          top_p: 0.9,
        }
      };

      const response = await fetch(url.toString(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
        signal: AbortSignal.timeout(300000), // 5 minutes timeout
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText || response.statusText}`);
      }

      if (!response.body) {
        throw new Error('Response body is empty');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n').filter(line => line.trim());

          for (const line of lines) {
            try {
              const data: OllamaStreamChunk = JSON.parse(line);
              
              if (data.message && data.message.content) {
                setStreamingContent(prev => prev + data.message.content);
              }

              if (data.done) {
                setIsStreaming(false);
                // Ici on pourrait appeler une callback pour sauvegarder la conversation
                return;
              }
            } catch (parseError) {
              console.warn('Failed to parse chunk:', line, parseError);
            }
          }
        }
      } finally {
        reader.releaseLock();
      }

    } catch (error) {
      console.error('Error in chat request:', error);
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          setError('Request timed out. Please try again.');
        } else if (error.message.includes('fetch')) {
          setError('Failed to connect to Ollama. Please check if Ollama is running.');
        } else {
          setError(error.message);
        }
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
    }
  }, [baseUrl]);

  return {
    sendMessage,
    isLoading,
    isStreaming,
    streamingContent,
    error,
    clearError,
  };
}