import { render } from '@testing-library/react';
import { ChatProvider } from '../context/ChatContext';

// Helper pour render avec ChatProvider
export const renderWithProvider = (ui, options = {}) => {
  const Wrapper = ({ children }) => (
    <ChatProvider>{children}</ChatProvider>
  );
  
  return render(ui, { wrapper: Wrapper, ...options });
};

// Mock data pour tests
export const mockMessage = {
  id: '1',
  text: 'Hello test',
  timestamp: new Date().toISOString(),
  user_id: 'enzo',
  is_user: true
};

export const mockResponse = {
  response: 'ACK::Hello test',
  timestamp: new Date().toISOString(),
  user_id: 'enzo',
  model: 'test-model',
  memory_saved: true
};

// Helper pour simuler WebSocket response
export const simulateWSResponse = (wsInstance, response) => {
  setTimeout(() => {
    wsInstance.onmessage?.({
      data: JSON.stringify(response)
    });
  }, 100);
};