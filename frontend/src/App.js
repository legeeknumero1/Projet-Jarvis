import React, { Suspense, lazy } from 'react';
import ErrorBoundary from './utils/errorBoundary';
import './App.css';

// Utiliser directement la version optimisée pour éviter erreurs de build
const CyberpunkJarvisInterface = lazy(() => 
  import('./components/CyberpunkJarvisInterfaceOptimized')
);

// Composant de loading optimisé
const LoadingFallback = () => (
  <div className="loading-container" style={{
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%)',
    color: '#ffffff',
    fontFamily: 'JetBrains Mono, monospace'
  }}>
    <div style={{
      textAlign: 'center',
      animation: 'pulse 2s infinite'
    }}>
      <div style={{
        fontSize: '3rem',
        marginBottom: '1rem',
        background: 'linear-gradient(45deg, #ff006e, #00d4ff)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        backgroundClip: 'text'
      }}>
        J.A.R.V.I.S
      </div>
      <div style={{
        color: '#b3b3b3'
      }}>
        Initialisation du système neural...
      </div>
      <div style={{
        marginTop: '2rem',
        display: 'flex',
        justifyContent: 'center',
        gap: '4px'
      }}>
        {[0, 1, 2].map(i => (
          <div
            key={i}
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: '#00d4ff',
              animation: `loading-dot 1.4s infinite ease-in-out both`,
              animationDelay: `${i * 0.16}s`
            }}
          />
        ))}
      </div>
    </div>
    <style jsx>{`
      @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
      }
      @keyframes loading-dot {
        0%, 80%, 100% { 
          transform: scale(0);
        }
        40% { 
          transform: scale(1);
        }
      }
    `}</style>
  </div>
);

function App() {
  return (
    <ErrorBoundary showDetails={process.env.NODE_ENV === 'development'}>
      <div className="App">
        <Suspense fallback={<LoadingFallback />}>
          <CyberpunkJarvisInterface />
        </Suspense>
      </div>
    </ErrorBoundary>
  );
}

export default App;