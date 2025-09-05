import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Mise à jour du state pour afficher l'UI de fallback
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Logger l'erreur (sans informations sensibles)
    console.error('🚨 React Error Boundary caught an error:', {
      error: error.toString(),
      componentStack: errorInfo.componentStack.slice(0, 500) // Limiter la taille
    });
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      // UI de fallback personnalisée
      return (
        <div className="error-boundary-container">
          <div className="error-boundary-content">
            <h1 className="error-title">⚠️ Erreur Détectée</h1>
            <p className="error-description">
              Une erreur inattendue s'est produite dans l'interface Jarvis.
            </p>
            
            <div className="error-actions">
              <button 
                className="error-button primary"
                onClick={() => window.location.reload()}
              >
                🔄 Recharger l'Interface
              </button>
              
              <button 
                className="error-button secondary"
                onClick={() => this.setState({ hasError: false, error: null, errorInfo: null })}
              >
                🔧 Réessayer
              </button>
            </div>
            
            {this.props.showDetails && (
              <details className="error-details">
                <summary>Détails Techniques</summary>
                <div className="error-stack">
                  <strong>Erreur:</strong>
                  <pre>{this.state.error && this.state.error.toString()}</pre>
                  
                  <strong>Stack:</strong>
                  <pre>{this.state.errorInfo && this.state.errorInfo.componentStack}</pre>
                </div>
              </details>
            )}
          </div>
          
          <style jsx>{`
            .error-boundary-container {
              display: flex;
              justify-content: center;
              align-items: center;
              min-height: 100vh;
              background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
              color: #ffffff;
              font-family: 'JetBrains Mono', monospace;
              padding: 20px;
            }
            
            .error-boundary-content {
              max-width: 600px;
              text-align: center;
              background: rgba(255, 255, 255, 0.05);
              border: 1px solid rgba(255, 0, 110, 0.3);
              border-radius: 12px;
              padding: 40px;
              backdrop-filter: blur(10px);
              box-shadow: 
                0 0 30px rgba(255, 0, 110, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            }
            
            .error-title {
              color: #ff006e;
              font-size: 2rem;
              margin-bottom: 1rem;
              text-shadow: 0 0 10px rgba(255, 0, 110, 0.5);
            }
            
            .error-description {
              color: #b3b3b3;
              margin-bottom: 2rem;
              line-height: 1.6;
            }
            
            .error-actions {
              display: flex;
              gap: 1rem;
              justify-content: center;
              margin-bottom: 2rem;
              flex-wrap: wrap;
            }
            
            .error-button {
              padding: 12px 24px;
              border: none;
              border-radius: 6px;
              font-family: inherit;
              font-weight: 600;
              cursor: pointer;
              transition: all 0.3s ease;
              text-decoration: none;
              display: inline-block;
            }
            
            .error-button.primary {
              background: linear-gradient(45deg, #ff006e, #8338ec);
              color: white;
              box-shadow: 0 4px 15px rgba(255, 0, 110, 0.3);
            }
            
            .error-button.primary:hover {
              transform: translateY(-2px);
              box-shadow: 0 8px 25px rgba(255, 0, 110, 0.4);
            }
            
            .error-button.secondary {
              background: transparent;
              color: #00d4ff;
              border: 1px solid #00d4ff;
            }
            
            .error-button.secondary:hover {
              background: rgba(0, 212, 255, 0.1);
              transform: translateY(-2px);
            }
            
            .error-details {
              text-align: left;
              margin-top: 2rem;
              color: #888;
              border-top: 1px solid rgba(255, 255, 255, 0.1);
              padding-top: 1rem;
            }
            
            .error-details summary {
              cursor: pointer;
              color: #00d4ff;
              margin-bottom: 1rem;
            }
            
            .error-details pre {
              background: rgba(0, 0, 0, 0.3);
              padding: 10px;
              border-radius: 4px;
              font-size: 0.8rem;
              overflow-x: auto;
              margin: 0.5rem 0;
              max-height: 200px;
              overflow-y: auto;
            }
            
            @media (max-width: 768px) {
              .error-boundary-content {
                padding: 20px;
              }
              
              .error-title {
                font-size: 1.5rem;
              }
              
              .error-actions {
                flex-direction: column;
                align-items: center;
              }
              
              .error-button {
                width: 100%;
                max-width: 200px;
              }
            }
          `}</style>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;