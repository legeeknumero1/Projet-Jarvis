import { render, screen, fireEvent } from '@testing-library/react';
import Composer from '../components/chat/Composer';

// Mock onSubmit function
const mockOnSubmit = jest.fn();

beforeEach(() => {
  mockOnSubmit.mockClear();
});

test('envoi message au Enter', () => {
  render(<Composer onSubmit={mockOnSubmit} disabled={false} />);
  
  // Chercher l'input par placeholder ou par role
  const input = screen.getByPlaceholderText(/Parle à Jarvis/i) || 
                screen.getByRole('textbox');
  
  // Taper message et appuyer Enter
  fireEvent.change(input, { target: { value: 'hello' } });
  fireEvent.keyDown(input, { key: 'Enter', shiftKey: false });
  
  expect(mockOnSubmit).toHaveBeenCalledWith('hello');
  expect(input.value).toBe(''); // Input vidé après envoi
});

test('Shift+Enter ajoute nouvelle ligne sans envoyer', () => {
  render(<Composer onSubmit={mockOnSubmit} disabled={false} />);
  
  const input = screen.getByPlaceholderText(/Parle à Jarvis/i) || 
                screen.getByRole('textbox');
  
  fireEvent.change(input, { target: { value: 'hello' } });
  fireEvent.keyDown(input, { key: 'Enter', shiftKey: true });
  
  // Ne doit pas envoyer avec Shift+Enter
  expect(mockOnSubmit).not.toHaveBeenCalled();
});

test('disabled bloque envoi', () => {
  render(<Composer onSubmit={mockOnSubmit} disabled={true} />);
  
  const input = screen.getByPlaceholderText(/Parle à Jarvis/i) || 
                screen.getByRole('textbox');
  
  fireEvent.change(input, { target: { value: 'hello' } });
  fireEvent.keyDown(input, { key: 'Enter', shiftKey: false });
  
  expect(mockOnSubmit).not.toHaveBeenCalled();
});

test('message vide ne peut pas être envoyé', () => {
  render(<Composer onSubmit={mockOnSubmit} disabled={false} />);
  
  const input = screen.getByPlaceholderText(/Parle à Jarvis/i) || 
                screen.getByRole('textbox');
  
  fireEvent.keyDown(input, { key: 'Enter', shiftKey: false });
  
  expect(mockOnSubmit).not.toHaveBeenCalled();
});