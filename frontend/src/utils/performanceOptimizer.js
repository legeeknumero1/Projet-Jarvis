/**
 * Utilitaires d'optimisation des performances React 2025
 * Outils pour améliorer les performances selon les standards 2025
 */

/**
 * Debounce optimisé pour les inputs
 * @param {Function} func - Fonction à débouncer
 * @param {number} delay - Délai en millisecondes
 * @returns {Function} - Fonction debouncée
 */
export const debounce = (func, delay = 300) => {
  let timeoutId;
  let lastArgs;
  let lastThis;
  
  const debouncedFunction = function(...args) {
    lastArgs = args;
    lastThis = this;
    
    clearTimeout(timeoutId);
    
    timeoutId = setTimeout(() => {
      func.apply(lastThis, lastArgs);
    }, delay);
  };
  
  // Fonction pour annuler le debounce
  debouncedFunction.cancel = () => {
    clearTimeout(timeoutId);
  };
  
  // Fonction pour exécuter immédiatement
  debouncedFunction.flush = () => {
    clearTimeout(timeoutId);
    if (lastArgs) {
      func.apply(lastThis, lastArgs);
    }
  };
  
  return debouncedFunction;
};

/**
 * Throttle optimisé pour les événements fréquents (scroll, resize)
 * @param {Function} func - Fonction à throttler
 * @param {number} limit - Limite en millisecondes
 * @returns {Function} - Fonction throttlée
 */
export const throttle = (func, limit = 100) => {
  let inThrottle;
  let lastFunc;
  let lastRan;
  
  return function(...args) {
    const context = this;
    
    if (!inThrottle) {
      func.apply(context, args);
      lastRan = Date.now();
      inThrottle = true;
    } else {
      clearTimeout(lastFunc);
      lastFunc = setTimeout(() => {
        if (Date.now() - lastRan >= limit) {
          func.apply(context, args);
          lastRan = Date.now();
        }
      }, limit - (Date.now() - lastRan));
    }
  };
};

/**
 * Gestionnaire de cache pour les calculs coûteux
 */
export class PerformanceCache {
  constructor(maxSize = 100, ttl = 300000) { // TTL par défaut: 5 minutes
    this.cache = new Map();
    this.maxSize = maxSize;
    this.ttl = ttl;
    this.timers = new Map();
  }

  /**
   * Récupérer une valeur du cache
   * @param {string} key - Clé du cache
   * @returns {*} - Valeur cachée ou undefined
   */
  get(key) {
    const item = this.cache.get(key);
    if (item) {
      // Vérifier si l'élément a expiré
      if (Date.now() - item.timestamp > this.ttl) {
        this.delete(key);
        return undefined;
      }
      return item.value;
    }
    return undefined;
  }

  /**
   * Stocker une valeur dans le cache
   * @param {string} key - Clé du cache
   * @param {*} value - Valeur à cacher
   */
  set(key, value) {
    // Supprimer l'élément le plus ancien si on dépasse la taille max
    if (this.cache.size >= this.maxSize && !this.cache.has(key)) {
      const firstKey = this.cache.keys().next().value;
      this.delete(firstKey);
    }

    // Ajouter l'élément avec timestamp
    this.cache.set(key, {
      value,
      timestamp: Date.now()
    });

    // Programmer la suppression automatique
    if (this.timers.has(key)) {
      clearTimeout(this.timers.get(key));
    }
    
    const timer = setTimeout(() => {
      this.delete(key);
    }, this.ttl);
    
    this.timers.set(key, timer);
  }

  /**
   * Supprimer un élément du cache
   * @param {string} key - Clé à supprimer
   */
  delete(key) {
    this.cache.delete(key);
    if (this.timers.has(key)) {
      clearTimeout(this.timers.get(key));
      this.timers.delete(key);
    }
  }

  /**
   * Vider tout le cache
   */
  clear() {
    this.cache.clear();
    this.timers.forEach(timer => clearTimeout(timer));
    this.timers.clear();
  }

  /**
   * Obtenir les statistiques du cache
   * @returns {Object} - Statistiques du cache
   */
  stats() {
    return {
      size: this.cache.size,
      maxSize: this.maxSize,
      hitRate: this._calculateHitRate(),
      oldestEntry: this._getOldestEntry()
    };
  }

  _calculateHitRate() {
    // Implémentation simplifiée - dans un vrai cas, on trackrait hits/misses
    return this.cache.size > 0 ? (this.cache.size / this.maxSize) : 0;
  }

  _getOldestEntry() {
    let oldest = null;
    let oldestTime = Date.now();
    
    for (const [key, item] of this.cache) {
      if (item.timestamp < oldestTime) {
        oldestTime = item.timestamp;
        oldest = key;
      }
    }
    
    return oldest;
  }
}

/**
 * Instance globale du cache de performance
 */
export const performanceCache = new PerformanceCache();

/**
 * Hook-like function pour memoiser des calculs coûteux avec cache externe
 * @param {Function} computation - Fonction de calcul
 * @param {Array} deps - Dépendances
 * @param {string} cacheKey - Clé de cache optionnelle
 * @returns {*} - Résultat du calcul
 */
export const memoizeWithCache = (computation, deps, cacheKey) => {
  const key = cacheKey || JSON.stringify(deps);
  
  // Vérifier le cache
  const cached = performanceCache.get(key);
  if (cached !== undefined) {
    return cached;
  }
  
  // Calculer et cacher
  const result = computation(...deps);
  performanceCache.set(key, result);
  
  return result;
};

/**
 * Optimiseur d'images pour réduire la charge réseau
 * @param {string} src - Source de l'image
 * @param {Object} options - Options d'optimisation
 * @returns {string} - URL optimisée
 */
export const optimizeImageSrc = (src, options = {}) => {
  const {
    width,
    height,
    quality = 80,
    format = 'webp',
    fallback = true
  } = options;

  // Si l'image est locale, retourner tel quel
  if (!src.startsWith('http')) {
    return src;
  }

  // Pour les services d'optimisation d'images (à adapter selon votre service)
  // Exemple avec un service générique
  const params = new URLSearchParams();
  
  if (width) params.append('w', width);
  if (height) params.append('h', height);
  if (quality) params.append('q', quality);
  if (format) params.append('f', format);

  // Retourner l'URL optimisée ou l'originale si pas de params
  return params.toString() ? `${src}?${params.toString()}` : src;
};

/**
 * Utilitaire pour mesurer les performances des composants
 */
export class ComponentPerformanceProfiler {
  constructor() {
    this.measurements = new Map();
  }

  /**
   * Commencer une mesure
   * @param {string} componentName - Nom du composant
   * @param {string} operation - Nom de l'opération
   */
  start(componentName, operation = 'render') {
    const key = `${componentName}.${operation}`;
    this.measurements.set(key, {
      startTime: performance.now(),
      componentName,
      operation
    });
  }

  /**
   * Terminer une mesure
   * @param {string} componentName - Nom du composant
   * @param {string} operation - Nom de l'opération
   * @returns {number} - Durée en millisecondes
   */
  end(componentName, operation = 'render') {
    const key = `${componentName}.${operation}`;
    const measurement = this.measurements.get(key);
    
    if (!measurement) {
      console.warn(`Aucune mesure trouvée pour ${key}`);
      return 0;
    }

    const duration = performance.now() - measurement.startTime;
    this.measurements.delete(key);

    // Logger les performances lentes
    if (duration > 16.67) { // Plus de 16.67ms = probablement un problème pour 60fps
      console.warn(`🐌 Performance lente détectée: ${key} = ${duration.toFixed(2)}ms`);
    } else if (duration > 8) {
      console.log(`⚡ Performance mesurée: ${key} = ${duration.toFixed(2)}ms`);
    }

    return duration;
  }

  /**
   * Profiler automatique avec décorateur de fonction
   * @param {string} componentName - Nom du composant
   * @param {string} operation - Nom de l'opération
   * @returns {Function} - Décorateur de fonction
   */
  profile(componentName, operation = 'render') {
    return (target, propertyName, descriptor) => {
      const method = descriptor.value;
      
      descriptor.value = function(...args) {
        this.start(componentName, operation);
        const result = method.apply(this, args);
        this.end(componentName, operation);
        return result;
      };
      
      return descriptor;
    };
  }

  /**
   * Obtenir les statistiques de performance
   * @returns {Object} - Statistiques
   */
  getStats() {
    return {
      activeMeasurements: this.measurements.size,
      measurements: Array.from(this.measurements.entries())
    };
  }
}

/**
 * Instance globale du profiler de performance
 */
export const performanceProfiler = new ComponentPerformanceProfiler();

/**
 * Utilitaire pour détecter les re-renders inutiles
 * @param {string} componentName - Nom du composant
 * @param {Object} props - Props du composant
 * @param {Object} prevProps - Props précédents
 */
export const detectUnnecessaryReRenders = (componentName, props, prevProps) => {
  if (!prevProps) return;

  const changedProps = {};
  let hasChanges = false;

  for (const key in props) {
    if (props[key] !== prevProps[key]) {
      changedProps[key] = {
        prev: prevProps[key],
        current: props[key]
      };
      hasChanges = true;
    }
  }

  if (hasChanges) {
    console.log(`🔄 Re-render ${componentName}:`, changedProps);
  } else {
    console.warn(`❌ Re-render inutile détecté pour ${componentName}`);
  }
};

/**
 * Optimiseur de listes pour la virtualisation
 * @param {Array} items - Liste d'éléments
 * @param {number} containerHeight - Hauteur du conteneur
 * @param {number} itemHeight - Hauteur d'un élément
 * @param {number} scrollTop - Position de scroll actuelle
 * @returns {Object} - Éléments visibles et indices
 */
export const virtualizeList = (items, containerHeight, itemHeight, scrollTop = 0) => {
  const totalHeight = items.length * itemHeight;
  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - 2); // Buffer de 2 éléments
  const endIndex = Math.min(
    items.length - 1,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + 2
  );

  const visibleItems = items.slice(startIndex, endIndex + 1).map((item, index) => ({
    item,
    index: startIndex + index,
    style: {
      position: 'absolute',
      top: (startIndex + index) * itemHeight,
      height: itemHeight
    }
  }));

  return {
    visibleItems,
    startIndex,
    endIndex,
    totalHeight,
    offsetY: startIndex * itemHeight
  };
};

/**
 * Gestionnaire d'événements optimisé pour éviter les memory leaks
 */
export class OptimizedEventManager {
  constructor() {
    this.listeners = new Map();
  }

  /**
   * Ajouter un écouteur d'événement
   * @param {EventTarget} element - Élément cible
   * @param {string} event - Type d'événement
   * @param {Function} handler - Gestionnaire d'événement
   * @param {Object} options - Options d'événement
   */
  addEventListener(element, event, handler, options = {}) {
    const key = `${element}_${event}_${handler.name || 'anonymous'}`;
    
    // Optimiser avec passive pour les événements de scroll/touch
    const optimizedOptions = {
      passive: ['scroll', 'wheel', 'touchstart', 'touchmove'].includes(event),
      ...options
    };

    element.addEventListener(event, handler, optimizedOptions);
    
    this.listeners.set(key, {
      element,
      event,
      handler,
      options: optimizedOptions
    });
  }

  /**
   * Supprimer un écouteur d'événement
   * @param {EventTarget} element - Élément cible
   * @param {string} event - Type d'événement
   * @param {Function} handler - Gestionnaire d'événement
   */
  removeEventListener(element, event, handler) {
    const key = `${element}_${event}_${handler.name || 'anonymous'}`;
    const listener = this.listeners.get(key);
    
    if (listener) {
      listener.element.removeEventListener(listener.event, listener.handler, listener.options);
      this.listeners.delete(key);
    }
  }

  /**
   * Nettoyer tous les écouteurs
   */
  cleanup() {
    for (const [key, listener] of this.listeners) {
      listener.element.removeEventListener(listener.event, listener.handler, listener.options);
    }
    this.listeners.clear();
  }

  /**
   * Obtenir les statistiques des écouteurs
   * @returns {Object} - Statistiques
   */
  getStats() {
    return {
      totalListeners: this.listeners.size,
      listenersByEvent: this._groupByEvent()
    };
  }

  _groupByEvent() {
    const groups = {};
    for (const [key, listener] of this.listeners) {
      if (!groups[listener.event]) {
        groups[listener.event] = 0;
      }
      groups[listener.event]++;
    }
    return groups;
  }
}

/**
 * Instance globale du gestionnaire d'événements optimisé
 */
export const eventManager = new OptimizedEventManager();