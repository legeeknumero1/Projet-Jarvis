import { render } from '@testing-library/react';
import App from './App';

test('app renders without crashing', () => {
  render(<App />);
  // Test simple : l'app se charge sans erreur
  expect(true).toBe(true);
});

test('app contains main container', () => {
  const { container } = render(<App />);
  expect(container.firstChild).toBeTruthy();
});