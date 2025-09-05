/**
 * Système de rapport de performance pour monitoring temps réel
 * Conforme aux standards Web Vitals 2025
 */

import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

class PerformanceReporter {
  constructor() {
    this.metrics = new Map();
    this.observers = [];
    this.isEnabled = process.env.NODE_ENV === 'development' || 
                    localStorage.getItem('jarvis_perf_monitoring') === 'true';
    
    if (this.isEnabled) {
      this.initializeWebVitals();
      this.initializeCustomMetrics();
    }
  }

  /**
   * Initialiser les métriques Web Vitals
   */
  initializeWebVitals() {
    const reportMetric = (metric) => {
      this.metrics.set(metric.name, {
        ...metric,
        timestamp: Date.now(),
        url: window.location.pathname
      });
      
      console.log(`📊 ${metric.name}:`, metric.value, metric.rating);
      
      // Alertes pour les métriques critiques
      if (metric.rating === 'poor') {
        console.warn(`⚠️ Performance critique: ${metric.name} = ${metric.value}${this.getMetricUnit(metric.name)}`);
      }
    };

    // Métriques Core Web Vitals
    getCLS(reportMetric);  // Cumulative Layout Shift
    getFID(reportMetric);  // First Input Delay
    getFCP(reportMetric);  // First Contentful Paint
    getLCP(reportMetric);  // Largest Contentful Paint
    getTTFB(reportMetric); // Time to First Byte
  }

  /**
   * Initialiser les métriques personnalisées
   */
  initializeCustomMetrics() {
    // Observer les Long Tasks (> 50ms)
    if ('PerformanceObserver' in window) {
      try {
        const longTaskObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.duration > 50) {
              console.warn(`🐌 Long Task détectée: ${entry.duration.toFixed(2)}ms`);
              this.recordCustomMetric('long-task', entry.duration, 'ms');
            }
          }
        });
        
        longTaskObserver.observe({ entryTypes: ['longtask'] });
        this.observers.push(longTaskObserver);
      } catch (e) {
        console.warn('Long Task Observer non supporté:', e);
      }

      // Observer les changements de layout
      try {
        const layoutShiftObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.value > 0.1) { // Seuil CLS critique
              console.warn(`📐 Layout Shift important: ${entry.value.toFixed(4)}`);
            }
          }
        });
        
        layoutShiftObserver.observe({ entryTypes: ['layout-shift'] });
        this.observers.push(layoutShiftObserver);
      } catch (e) {
        console.warn('Layout Shift Observer non supporté:', e);
      }
    }

    // Monitoring de la mémoire
    this.startMemoryMonitoring();
    
    // Monitoring du frame rate
    this.startFrameRateMonitoring();
  }

  /**
   * Monitoring de l'utilisation mémoire
   */
  startMemoryMonitoring() {
    if (!('memory' in performance)) return;

    const checkMemory = () => {
      const memory = performance.memory;
      const usedMB = Math.round(memory.usedJSHeapSize / 1024 / 1024);
      const limitMB = Math.round(memory.jsHeapSizeLimit / 1024 / 1024);
      const usagePercent = (usedMB / limitMB) * 100;

      this.recordCustomMetric('memory-usage', usedMB, 'MB');
      
      if (usagePercent > 80) {
        console.warn(`🧠 Utilisation mémoire élevée: ${usedMB}MB (${usagePercent.toFixed(1)}%)`);
      }
    };

    checkMemory();
    setInterval(checkMemory, 30000); // Check toutes les 30 secondes
  }

  /**
   * Monitoring du frame rate
   */
  startFrameRateMonitoring() {
    let frameCount = 0;
    let lastTime = performance.now();
    
    const measureFPS = () => {
      frameCount++;
      const currentTime = performance.now();
      
      if (currentTime >= lastTime + 1000) {
        const fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
        this.recordCustomMetric('fps', fps, 'fps');
        
        if (fps < 30) {
          console.warn(`🎮 FPS faible détecté: ${fps} fps`);
        }
        
        frameCount = 0;
        lastTime = currentTime;
      }
      
      requestAnimationFrame(measureFPS);
    };
    
    requestAnimationFrame(measureFPS);
  }

  /**
   * Enregistrer une métrique personnalisée
   */
  recordCustomMetric(name, value, unit = '') {
    this.metrics.set(name, {
      name,
      value,
      unit,
      timestamp: Date.now(),
      url: window.location.pathname
    });
  }

  /**
   * Mesurer le temps d'exécution d'une fonction
   */
  measureFunction(name, fn) {
    const start = performance.now();
    const result = fn();
    const duration = performance.now() - start;
    
    this.recordCustomMetric(`function-${name}`, duration, 'ms');
    
    if (duration > 16.67) { // Plus d'une frame à 60fps
      console.warn(`⏱️ Fonction lente: ${name} = ${duration.toFixed(2)}ms`);
    }
    
    return result;
  }

  /**
   * Mesurer le temps d'exécution d'une fonction async
   */
  async measureAsyncFunction(name, fn) {
    const start = performance.now();
    const result = await fn();
    const duration = performance.now() - start;
    
    this.recordCustomMetric(`async-${name}`, duration, 'ms');
    
    if (duration > 100) { // Seuil pour opérations async
      console.warn(`⏱️ Opération async lente: ${name} = ${duration.toFixed(2)}ms`);
    }
    
    return result;
  }

  /**
   * Créer un décorateur de performance pour les composants React
   */
  createComponentProfiler(componentName) {
    return {
      onRender: (id, phase, actualDuration) => {
        this.recordCustomMetric(`react-${componentName}-${phase}`, actualDuration, 'ms');
        
        if (actualDuration > 16.67) {
          console.warn(`⚛️ Re-render lent: ${componentName} (${phase}) = ${actualDuration.toFixed(2)}ms`);
        }
      }
    };
  }

  /**
   * Obtenir le résumé des performances
   */
  getPerformanceSummary() {
    const summary = {
      webVitals: {},
      customMetrics: {},
      issues: [],
      score: 0
    };

    // Compiler les Web Vitals
    ['CLS', 'FID', 'FCP', 'LCP', 'TTFB'].forEach(name => {
      if (this.metrics.has(name)) {
        const metric = this.metrics.get(name);
        summary.webVitals[name] = {
          value: metric.value,
          rating: metric.rating,
          unit: this.getMetricUnit(name)
        };
        
        if (metric.rating === 'poor') {
          summary.issues.push(`${name} est critique (${metric.value}${this.getMetricUnit(name)})`);
        }
      }
    });

    // Compiler les métriques personnalisées
    for (const [name, metric] of this.metrics) {
      if (!['CLS', 'FID', 'FCP', 'LCP', 'TTFB'].includes(name)) {
        summary.customMetrics[name] = metric;
      }
    }

    // Calculer un score global (0-100)
    summary.score = this.calculatePerformanceScore(summary);

    return summary;
  }

  /**
   * Calculer un score de performance global
   */
  calculatePerformanceScore(summary) {
    let score = 100;
    const webVitals = summary.webVitals;

    // Pénalités pour chaque métrique critique
    Object.values(webVitals).forEach(metric => {
      switch(metric.rating) {
        case 'poor':
          score -= 20;
          break;
        case 'needs-improvement':
          score -= 10;
          break;
        default:
          // good rating, pas de pénalité
      }
    });

    // Pénalités pour métriques personnalisées
    if (this.metrics.has('fps')) {
      const fps = this.metrics.get('fps').value;
      if (fps < 30) score -= 15;
      else if (fps < 45) score -= 10;
    }

    if (this.metrics.has('memory-usage')) {
      const memoryMB = this.metrics.get('memory-usage').value;
      if (memoryMB > 200) score -= 10;
      else if (memoryMB > 150) score -= 5;
    }

    return Math.max(0, score);
  }

  /**
   * Obtenir l'unité d'une métrique
   */
  getMetricUnit(metricName) {
    const units = {
      'CLS': '',
      'FID': 'ms',
      'FCP': 'ms',
      'LCP': 'ms',
      'TTFB': 'ms'
    };
    return units[metricName] || '';
  }

  /**
   * Exporter les données de performance
   */
  exportMetrics() {
    const data = {
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent,
      summary: this.getPerformanceSummary(),
      rawMetrics: Object.fromEntries(this.metrics)
    };

    // Option 1: Console pour développement
    console.table(data.summary.webVitals);
    console.log('📊 Export complet des métriques:', data);

    // Option 2: Télécharger en JSON
    if (localStorage.getItem('jarvis_perf_download') === 'true') {
      this.downloadMetrics(data);
    }

    // Option 3: Envoyer à un service d'analytics (à implémenter)
    // this.sendToAnalytics(data);

    return data;
  }

  /**
   * Télécharger les métriques en JSON
   */
  downloadMetrics(data) {
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `jarvis-performance-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  /**
   * Nettoyer les observers
   */
  cleanup() {
    this.observers.forEach(observer => {
      try {
        observer.disconnect();
      } catch (e) {
        console.warn('Erreur cleanup observer:', e);
      }
    });
    this.observers = [];
    this.metrics.clear();
  }

  /**
   * Interface de contrôle via console
   */
  getDebugInterface() {
    return {
      summary: () => this.getPerformanceSummary(),
      export: () => this.exportMetrics(),
      enable: () => {
        localStorage.setItem('jarvis_perf_monitoring', 'true');
        window.location.reload();
      },
      disable: () => {
        localStorage.removeItem('jarvis_perf_monitoring');
        this.cleanup();
      },
      enableDownload: () => {
        localStorage.setItem('jarvis_perf_download', 'true');
        console.log('📥 Téléchargement automatique activé');
      },
      metrics: () => Object.fromEntries(this.metrics)
    };
  }
}

// Instance globale
export const performanceReporter = new PerformanceReporter();

// Interface debug globale pour la console
if (typeof window !== 'undefined') {
  window.JarvisPerf = performanceReporter.getDebugInterface();
  console.log('🔧 Interface de debug disponible: JarvisPerf');
  console.log('Commands: JarvisPerf.summary(), JarvisPerf.export(), JarvisPerf.enable()');
}

// Hook React pour utiliser le performance reporter
export const usePerformanceReporter = () => {
  const measureRender = (componentName, fn) => {
    return performanceReporter.measureFunction(`react-${componentName}`, fn);
  };

  const measureAsyncRender = async (componentName, fn) => {
    return await performanceReporter.measureAsyncFunction(`react-${componentName}`, fn);
  };

  return {
    measureRender,
    measureAsyncRender,
    recordMetric: (name, value, unit) => performanceReporter.recordCustomMetric(name, value, unit),
    getSummary: () => performanceReporter.getPerformanceSummary(),
    createProfiler: (componentName) => performanceReporter.createComponentProfiler(componentName)
  };
};

export default performanceReporter;