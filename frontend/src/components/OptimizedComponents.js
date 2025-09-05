import React, { memo, useMemo, useCallback, useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { debounce, virtualizeList } from '../utils/performanceOptimizer';

/**
 * Composant VirtualizedList optimisé pour les grandes listes
 * Implémente la virtualisation pour améliorer les performances
 */
export const VirtualizedMessageList = memo(({ messages, containerHeight = 400, itemHeight = 80 }) => {
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef(null);

  // Gestionnaire de scroll optimisé avec throttle
  const handleScroll = useCallback(
    debounce((e) => {
      setScrollTop(e.target.scrollTop);
    }, 16), // 16ms = 60fps
    []
  );

  // Virtualisation des messages
  const virtualizedData = useMemo(() => {
    if (!messages.length) return { visibleItems: [], totalHeight: 0 };
    
    return virtualizeList(messages, containerHeight, itemHeight, scrollTop);
  }, [messages, containerHeight, itemHeight, scrollTop]);

  return (
    <div
      ref={containerRef}
      style={{
        height: containerHeight,
        overflow: 'auto',
        position: 'relative'
      }}
      onScroll={handleScroll}
    >
      <div style={{ height: virtualizedData.totalHeight, position: 'relative' }}>
        {virtualizedData.visibleItems.map(({ item: message, index, style }) => (
          <div key={message.id || index} style={style}>
            <MessageItem message={message} />
          </div>
        ))}
      </div>
    </div>
  );
});

VirtualizedMessageList.displayName = 'VirtualizedMessageList';

/**
 * Composant MessageItem optimisé avec React.memo
 */
const MessageItem = memo(({ message }) => {
  const messageVariants = useMemo(() => ({
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 }
  }), []);

  return (
    <motion.div
      className={`message-item ${message.type} ${message.isError ? 'error' : ''}`}
      variants={messageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={{ duration: 0.3 }}
    >
      <div className="message-avatar">
        {message.type === 'user' ? 'E' : 'J'}
      </div>
      <div className="message-content">
        <div className="message-header">
          <span className="sender">
            {message.type === 'user' ? 'Enzo' : 'J.A.R.V.I.S'}
          </span>
          <span className="timestamp">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
        </div>
        <div className="message-text">{message.content}</div>
      </div>
    </motion.div>
  );
});

MessageItem.displayName = 'MessageItem';

/**
 * Composant OptimizedInput avec debounce intégré
 */
export const OptimizedInput = memo(({ 
  value, 
  onChange, 
  onSubmit, 
  placeholder, 
  disabled = false,
  debounceMs = 300,
  maxLength = 5000
}) => {
  const [internalValue, setInternalValue] = useState(value || '');
  const inputRef = useRef(null);

  // Debounced onChange pour éviter trop d'appels
  const debouncedOnChange = useMemo(
    () => debounce((newValue) => {
      if (onChange) onChange(newValue);
    }, debounceMs),
    [onChange, debounceMs]
  );

  // Gestionnaire de changement interne
  const handleChange = useCallback((e) => {
    const newValue = e.target.value.substring(0, maxLength);
    setInternalValue(newValue);
    debouncedOnChange(newValue);
  }, [debouncedOnChange, maxLength]);

  // Gestionnaire de soumission optimisé
  const handleSubmit = useCallback((e) => {
    e.preventDefault();
    if (onSubmit && internalValue.trim()) {
      onSubmit(internalValue.trim());
      setInternalValue('');
    }
  }, [onSubmit, internalValue]);

  // Gestionnaire de touche optimisé
  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }, [handleSubmit]);

  // Auto-resize du textarea
  useEffect(() => {
    if (inputRef.current) {
      const element = inputRef.current;
      element.style.height = 'auto';
      element.style.height = Math.min(element.scrollHeight, 150) + 'px';
    }
  }, [internalValue]);

  // Sync avec la prop value si elle change
  useEffect(() => {
    if (value !== internalValue) {
      setInternalValue(value || '');
    }
  }, [value]);

  return (
    <form onSubmit={handleSubmit} className="optimized-input-form">
      <textarea
        ref={inputRef}
        value={internalValue}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        rows={1}
        className="optimized-textarea"
        aria-label="Zone de saisie de message"
      />
      <div className="input-footer">
        <span className="character-count">
          {internalValue.length}/{maxLength}
        </span>
        <button
          type="submit"
          disabled={disabled || !internalValue.trim()}
          className="submit-button"
          aria-label="Envoyer le message"
        >
          ⚡
        </button>
      </div>
    </form>
  );
});

OptimizedInput.displayName = 'OptimizedInput';

/**
 * Composant StatusIndicator optimisé
 */
export const StatusIndicator = memo(({ 
  isConnected, 
  isWsConnected, 
  isListening, 
  isSpeaking,
  reconnectAttempts = 0,
  maxReconnectAttempts = 5
}) => {
  // Status calculé avec useMemo pour éviter recalculs inutiles
  const statusInfo = useMemo(() => {
    if (isWsConnected) {
      return {
        text: 'En ligne (WebSocket)',
        color: '#00ff88',
        icon: '🟢'
      };
    }
    
    if (isConnected) {
      return {
        text: 'En ligne (REST)',
        color: '#ffaa00',
        icon: '🟡'
      };
    }

    if (reconnectAttempts > 0) {
      return {
        text: `Reconnexion ${reconnectAttempts}/${maxReconnectAttempts}`,
        color: '#ff6600',
        icon: '🔄'
      };
    }
    
    return {
      text: 'Hors ligne',
      color: '#ff4444',
      icon: '🔴'
    };
  }, [isConnected, isWsConnected, reconnectAttempts, maxReconnectAttempts]);

  return (
    <div className="status-indicator">
      <div 
        className="status-dot" 
        style={{ backgroundColor: statusInfo.color }}
        title={statusInfo.text}
      />
      <span className="status-text">{statusInfo.text}</span>
      
      {isListening && (
        <motion.div
          className="activity-indicator listening"
          animate={{ scale: [1, 1.2, 1] }}
          transition={{ repeat: Infinity, duration: 1 }}
        >
          🎤
        </motion.div>
      )}
      
      {isSpeaking && (
        <motion.div
          className="activity-indicator speaking"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ repeat: Infinity, duration: 0.8 }}
        >
          🔊
        </motion.div>
      )}
    </div>
  );
});

StatusIndicator.displayName = 'StatusIndicator';

/**
 * Composant PerformanceMonitor pour le développement
 */
export const PerformanceMonitor = memo(({ enabled = process.env.NODE_ENV === 'development' }) => {
  const [metrics, setMetrics] = useState({
    renderCount: 0,
    averageRenderTime: 0,
    lastRenderTime: 0,
    memoryUsage: 0
  });

  const renderStartTime = useRef(performance.now());
  const renderTimes = useRef([]);

  useEffect(() => {
    if (!enabled) return;

    const endTime = performance.now();
    const renderTime = endTime - renderStartTime.current;
    
    renderTimes.current.push(renderTime);
    if (renderTimes.current.length > 100) {
      renderTimes.current.shift(); // Garder seulement les 100 dernières mesures
    }

    const averageTime = renderTimes.current.reduce((a, b) => a + b, 0) / renderTimes.current.length;
    
    setMetrics(prev => ({
      ...prev,
      renderCount: prev.renderCount + 1,
      averageRenderTime: averageTime,
      lastRenderTime: renderTime,
      memoryUsage: performance.memory ? performance.memory.usedJSHeapSize / 1024 / 1024 : 0
    }));

    renderStartTime.current = performance.now();
  });

  if (!enabled) return null;

  return (
    <div className="performance-monitor" style={{
      position: 'fixed',
      top: 10,
      right: 10,
      background: 'rgba(0, 0, 0, 0.8)',
      color: 'white',
      padding: '10px',
      borderRadius: '4px',
      fontSize: '12px',
      fontFamily: 'monospace',
      zIndex: 9999
    }}>
      <div>Renders: {metrics.renderCount}</div>
      <div>Last: {metrics.lastRenderTime.toFixed(2)}ms</div>
      <div>Avg: {metrics.averageRenderTime.toFixed(2)}ms</div>
      {metrics.memoryUsage > 0 && (
        <div>Memory: {metrics.memoryUsage.toFixed(1)}MB</div>
      )}
      {metrics.lastRenderTime > 16.67 && (
        <div style={{ color: 'red' }}>⚠️ Slow render</div>
      )}
    </div>
  );
});

PerformanceMonitor.displayName = 'PerformanceMonitor';

/**
 * Composant LazyImage avec loading progressif
 */
export const LazyImage = memo(({ 
  src, 
  alt, 
  width, 
  height, 
  className,
  fallback = '/placeholder.svg',
  ...props 
}) => {
  const [imageSrc, setImageSrc] = useState(fallback);
  const [isLoaded, setIsLoaded] = useState(false);
  const [isError, setIsError] = useState(false);
  const imgRef = useRef(null);

  // Intersection Observer pour lazy loading
  useEffect(() => {
    if (!imgRef.current || !src) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            setImageSrc(src);
            observer.unobserve(entry.target);
          }
        });
      },
      {
        rootMargin: '50px' // Charger 50px avant que l'image soit visible
      }
    );

    observer.observe(imgRef.current);

    return () => {
      if (imgRef.current) {
        observer.unobserve(imgRef.current);
      }
    };
  }, [src]);

  const handleLoad = useCallback(() => {
    setIsLoaded(true);
    setIsError(false);
  }, []);

  const handleError = useCallback(() => {
    setIsError(true);
    setImageSrc(fallback);
  }, [fallback]);

  return (
    <div 
      className={`lazy-image-container ${className || ''}`}
      style={{ width, height }}
    >
      <img
        ref={imgRef}
        src={imageSrc}
        alt={alt}
        onLoad={handleLoad}
        onError={handleError}
        style={{
          opacity: isLoaded && !isError ? 1 : 0.7,
          transition: 'opacity 0.3s ease',
          filter: !isLoaded ? 'blur(2px)' : 'none',
          width: '100%',
          height: '100%',
          objectFit: 'cover'
        }}
        {...props}
      />
      
      {!isLoaded && !isError && (
        <div className="loading-overlay" style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'rgba(0, 0, 0, 0.1)'
        }}>
          <div className="loading-spinner">⟳</div>
        </div>
      )}
    </div>
  );
});

LazyImage.displayName = 'LazyImage';

/**
 * HOC pour mesurer les performances des composants
 */
export const withPerformanceTracking = (WrappedComponent, componentName) => {
  const PerformanceTrackedComponent = memo((props) => {
    const renderStart = useRef(performance.now());
    const [renderTime, setRenderTime] = useState(0);

    useEffect(() => {
      const endTime = performance.now();
      const duration = endTime - renderStart.current;
      setRenderTime(duration);

      if (duration > 16.67) {
        console.warn(`🐌 Slow render detected: ${componentName} = ${duration.toFixed(2)}ms`);
      }

      renderStart.current = performance.now();
    });

    return <WrappedComponent {...props} />;
  });

  PerformanceTrackedComponent.displayName = `withPerformanceTracking(${componentName})`;
  return PerformanceTrackedComponent;
};