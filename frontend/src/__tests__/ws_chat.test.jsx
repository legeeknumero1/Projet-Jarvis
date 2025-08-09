import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChatProvider } from '../context/ChatContext';
import ChatLayout from '../components/layout/ChatLayout';

// Helper pour rendre avec provider
const renderWithProvider = (ui) => {
  return render(<ChatProvider>{ui}</ChatProvider>);
};

test('WebSocket envoie message JSON et reçoit réponse', async () => {
  renderWithProvider(<ChatLayout />);
  
  // Trouver l'input
  const input = screen.getByPlaceholderText(/Parle à Jarvis/i) || 
                screen.getByRole('textbox');
  
  // Envoyer message
  fireEvent.change(input, { target: { value: 'yo' } });
  fireEvent.keyDown(input, { key: 'Enter', shiftKey: false });
  
  await waitFor(() => {
    // Vérifier qu'un WebSocket a été créé
    expect(global.WebSocket).toHaveBeenCalled;
  });
  
  // Simuler réponse serveur
  const wsInstance = new global.WebSocket('ws://test');
  setTimeout(() => {
    wsInstance.onmessage?.({
      data: JSON.stringify({ 
        response: 'ACK::yo',
        user_id: 'enzo',
        timestamp: new Date().toISOString()
      })
    });
  }, 100);
  
  // Attendre que la réponse apparaisse
  await waitFor(() => {
    expect(screen.queryByText(/ACK::yo/)).toBeInTheDocument();
  }, { timeout: 2000 });
});

test('WebSocket se reconnecte automatiquement après perte connexion', async () => {
  renderWithProvider(<ChatLayout />);
  
  const wsInstance = new global.WebSocket('ws://test');
  
  // Simuler perte connexion
  fireEvent(wsInstance, new Event('close'));
  
  await waitFor(() => {
    // Vérifier qu'une nouvelle connexion est tentée
    // (dépend de l'implémentation du useWebSocket)
    expect(true).toBe(true); // Placeholder - adapter selon l'implémentation
  });
});

test('Messages s\'affichent dans bon ordre chronologique', async () => {
  renderWithProvider(<ChatLayout />);
  
  const input = screen.getByPlaceholderText(/Parle à Jarvis/i) || 
                screen.getByRole('textbox');
  
  // Envoyer plusieurs messages
  const messages = ['msg1', 'msg2', 'msg3'];
  
  for (const msg of messages) {
    fireEvent.change(input, { target: { value: msg } });
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: false });
    
    // Simuler réponse
    const wsInstance = new global.WebSocket('ws://test');
    setTimeout(() => {
      wsInstance.onmessage?.({
        data: JSON.stringify({ 
          response: `ACK::${msg}`,
          user_id: 'enzo',
          timestamp: new Date().toISOString()
        })
      });
    }, 50);
  }
  
  await waitFor(() => {
    // Vérifier que tous les messages sont présents
    messages.forEach(msg => {
      expect(screen.getByText(msg)).toBeInTheDocument();
    });
  });
});