import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
// Performance reporter importé automatiquement pour initialisation
import './performance/PerformanceReporter';

// Configuration React 18 avec optimisations de performance
const root = ReactDOM.createRoot(document.getElementById('root'));

// Démarrer le monitoring de performance en développement
if (process.env.NODE_ENV === 'development') {
  console.log('🚀 Jarvis Frontend - Mode Développement');
  console.log('📊 Performance monitoring activé');
  console.log('🔧 Utilisez JarvisPerf dans la console pour les métriques');
}

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Report Web Vitals pour le monitoring
const reportWebVitals = (onPerfEntry) => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(onPerfEntry);
      getFID(onPerfEntry);
      getFCP(onPerfEntry);
      getLCP(onPerfEntry);
      getTTFB(onPerfEntry);
    });
  }
};

// Envoyer les métriques vers le performance reporter
reportWebVitals(console.log);