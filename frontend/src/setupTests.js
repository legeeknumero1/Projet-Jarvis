// jest-dom adds custom jest matchers for asserting on DOM nodes.
import '@testing-library/jest-dom';

// Mock WebSocket pour tests
class WSMock {
  constructor(url) {
    this.url = url;
    this.sent = [];
    this.readyState = 1; // OPEN
    // Simuler connexion async
    setTimeout(() => this.onopen?.(), 0);
  }
  
  send(msg) {
    this.sent.push(msg);
  }
  
  close() {
    this.readyState = 3; // CLOSED
    this.onclose?.();
  }
}

global.WebSocket = WSMock;

// Mock SpeechRecognition si utilisé
global.SpeechRecognition = global.webkitSpeechRecognition = undefined;