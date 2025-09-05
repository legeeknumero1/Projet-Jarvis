/**
 * Constantes d'animation optimisées pour les performances
 * Réduire les recalculs et améliorer la fluidité selon standards 2025
 */

// Durées d'animation optimisées pour 60fps
export const ANIMATION_DURATIONS = {
  FAST: 0.15,      // 150ms - micro-interactions
  NORMAL: 0.3,     // 300ms - transitions standard
  SLOW: 0.5,       // 500ms - animations importantes
  VERY_SLOW: 1.0   // 1000ms - animations d'entrée
};

// Easing curves optimisées pour les performances
export const EASING = {
  LINEAR: "linear",
  EASE: "ease",
  EASE_IN: "easeIn",
  EASE_OUT: "easeOut",
  EASE_IN_OUT: "easeInOut",
  // Easing personnalisées pour Framer Motion
  SPRING: {
    type: "spring",
    stiffness: 100,
    damping: 10
  },
  SMOOTH_SPRING: {
    type: "spring",
    stiffness: 260,
    damping: 20
  },
  BOUNCY: {
    type: "spring",
    stiffness: 400,
    damping: 17
  }
};

// Variants d'animation réutilisables
export const ANIMATION_VARIANTS = {
  // Fade animations
  FADE_IN: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 }
  },
  
  FADE_IN_UP: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 }
  },
  
  FADE_IN_DOWN: {
    initial: { opacity: 0, y: -20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: 20 }
  },
  
  // Scale animations
  SCALE_IN: {
    initial: { opacity: 0, scale: 0.8 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.8 }
  },
  
  SCALE_BOUNCE: {
    initial: { scale: 0 },
    animate: { scale: 1 },
    exit: { scale: 0 }
  },
  
  // Slide animations
  SLIDE_LEFT: {
    initial: { x: -100, opacity: 0 },
    animate: { x: 0, opacity: 1 },
    exit: { x: 100, opacity: 0 }
  },
  
  SLIDE_RIGHT: {
    initial: { x: 100, opacity: 0 },
    animate: { x: 0, opacity: 1 },
    exit: { x: -100, opacity: 0 }
  },
  
  // Rotation animations
  ROTATE_IN: {
    initial: { rotate: -180, opacity: 0 },
    animate: { rotate: 0, opacity: 1 },
    exit: { rotate: 180, opacity: 0 }
  },
  
  // Complex animations pour Jarvis
  JARVIS_ORB: {
    initial: { 
      scale: 0,
      rotate: 0,
      opacity: 0
    },
    animate: { 
      scale: 1,
      rotate: 360,
      opacity: 1,
      transition: {
        scale: EASING.SMOOTH_SPRING,
        rotate: { repeat: Infinity, duration: 10, ease: "linear" },
        opacity: { duration: ANIMATION_DURATIONS.NORMAL }
      }
    },
    exit: { 
      scale: 0,
      opacity: 0,
      transition: { duration: ANIMATION_DURATIONS.FAST }
    }
  },
  
  MESSAGE_BUBBLE: {
    initial: { 
      opacity: 0, 
      y: 50, 
      scale: 0.8 
    },
    animate: { 
      opacity: 1, 
      y: 0, 
      scale: 1,
      transition: {
        duration: ANIMATION_DURATIONS.NORMAL,
        ease: EASING.EASE_OUT
      }
    },
    exit: { 
      opacity: 0, 
      scale: 0.8,
      transition: { duration: ANIMATION_DURATIONS.FAST }
    }
  },
  
  TYPING_INDICATOR: {
    animate: {
      opacity: [0, 1, 0],
      transition: {
        repeat: Infinity,
        duration: 1,
        ease: EASING.EASE_IN_OUT
      }
    }
  }
};

// Transitions optimisées pour différents types de contenu
export const TRANSITIONS = {
  DEFAULT: {
    duration: ANIMATION_DURATIONS.NORMAL,
    ease: EASING.EASE_OUT
  },
  
  QUICK: {
    duration: ANIMATION_DURATIONS.FAST,
    ease: EASING.EASE_OUT
  },
  
  SMOOTH: {
    duration: ANIMATION_DURATIONS.NORMAL,
    ease: EASING.EASE_IN_OUT
  },
  
  SPRING: EASING.SMOOTH_SPRING,
  
  STAGGER_CHILDREN: {
    staggerChildren: 0.1,
    delayChildren: 0.1
  },
  
  // Transitions spécifiques pour les listes
  LIST_ITEM: {
    duration: ANIMATION_DURATIONS.FAST,
    ease: EASING.EASE_OUT
  },
  
  // Transitions pour les modals/overlays
  MODAL: {
    duration: ANIMATION_DURATIONS.NORMAL,
    ease: EASING.EASE_OUT
  }
};

// Configurations d'animation pour les interactions
export const HOVER_ANIMATIONS = {
  SCALE_UP: {
    scale: 1.05,
    transition: { duration: ANIMATION_DURATIONS.FAST }
  },
  
  LIFT: {
    y: -2,
    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
    transition: { duration: ANIMATION_DURATIONS.FAST }
  },
  
  GLOW: {
    boxShadow: "0 0 20px rgba(0, 212, 255, 0.5)",
    transition: { duration: ANIMATION_DURATIONS.FAST }
  }
};

export const TAP_ANIMATIONS = {
  SCALE_DOWN: {
    scale: 0.95,
    transition: { duration: ANIMATION_DURATIONS.FAST }
  },
  
  SHRINK: {
    scale: 0.98,
    transition: { duration: 0.1 }
  }
};

// Animations spécifiques à Jarvis
export const JARVIS_ANIMATIONS = {
  NEURAL_PULSE: {
    animate: {
      scale: [1, 1.2, 1],
      opacity: [0.6, 1, 0.6],
      boxShadow: [
        "0 0 0 0 rgba(0, 212, 255, 0.7)",
        "0 0 0 10px rgba(0, 212, 255, 0)",
        "0 0 0 0 rgba(0, 212, 255, 0)"
      ]
    },
    transition: {
      repeat: Infinity,
      duration: 2,
      ease: EASING.EASE_IN_OUT
    }
  },
  
  DATA_STREAM: {
    animate: {
      backgroundPosition: ["0% 0%", "100% 100%"]
    },
    transition: {
      repeat: Infinity,
      duration: 3,
      ease: "linear"
    }
  },
  
  HOLOGRAPHIC: {
    animate: {
      background: [
        "linear-gradient(45deg, #ff006e, #8338ec)",
        "linear-gradient(45deg, #00d4ff, #ff006e)",
        "linear-gradient(45deg, #8338ec, #00d4ff)",
        "linear-gradient(45deg, #ff006e, #8338ec)"
      ]
    },
    transition: {
      repeat: Infinity,
      duration: 4,
      ease: "linear"
    }
  }
};

// Configurations de performance pour les animations
export const PERFORMANCE_CONFIG = {
  // Réduire les animations sur les appareils moins puissants
  REDUCED_MOTION_QUERY: "(prefers-reduced-motion: reduce)",
  
  // Frames par seconde cibles
  TARGET_FPS: 60,
  FRAME_BUDGET: 16.67, // ms par frame pour 60fps
  
  // Seuils de performance
  PERFORMANCE_THRESHOLDS: {
    GOOD: 16.67,    // < 16.67ms par frame
    MODERATE: 33.33, // < 33.33ms par frame (30fps)
    POOR: 50        // > 50ms par frame
  },
  
  // Optimisations automatiques
  AUTO_OPTIMIZE: {
    // Désactiver les animations complexes si les performances sont mauvaises
    DISABLE_COMPLEX_ON_POOR_PERF: true,
    
    // Réduire la qualité des animations sur mobile
    REDUCE_QUALITY_ON_MOBILE: true,
    
    // Limiter le nombre d'animations simultanées
    MAX_CONCURRENT_ANIMATIONS: 10
  }
};

// Présets d'animation pour différents types de composants
export const COMPONENT_PRESETS = {
  BUTTON: {
    whileHover: HOVER_ANIMATIONS.SCALE_UP,
    whileTap: TAP_ANIMATIONS.SCALE_DOWN,
    transition: TRANSITIONS.QUICK
  },
  
  CARD: {
    initial: ANIMATION_VARIANTS.FADE_IN_UP.initial,
    animate: ANIMATION_VARIANTS.FADE_IN_UP.animate,
    exit: ANIMATION_VARIANTS.FADE_IN_UP.exit,
    whileHover: HOVER_ANIMATIONS.LIFT,
    transition: TRANSITIONS.SMOOTH
  },
  
  MODAL: {
    initial: { opacity: 0, scale: 0.8 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.8 },
    transition: TRANSITIONS.MODAL
  },
  
  LIST_ITEM: {
    initial: ANIMATION_VARIANTS.FADE_IN_UP.initial,
    animate: ANIMATION_VARIANTS.FADE_IN_UP.animate,
    exit: ANIMATION_VARIANTS.FADE_IN_UP.exit,
    transition: TRANSITIONS.LIST_ITEM
  }
};

// Utilitaires pour la gestion des animations
export const ANIMATION_UTILS = {
  // Vérifier si l'utilisateur préfère les animations réduites
  shouldReduceMotion: () => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia(PERFORMANCE_CONFIG.REDUCED_MOTION_QUERY).matches;
  },
  
  // Adapter les animations selon les performances
  getOptimizedTransition: (baseTransition, currentFPS = 60) => {
    const { TARGET_FPS, PERFORMANCE_THRESHOLDS } = PERFORMANCE_CONFIG;
    
    if (currentFPS >= TARGET_FPS) {
      return baseTransition;
    }
    
    if (currentFPS < PERFORMANCE_THRESHOLDS.POOR) {
      // Performances très mauvaises : animations simplifiées
      return {
        duration: baseTransition.duration * 0.5,
        ease: EASING.LINEAR
      };
    }
    
    if (currentFPS < PERFORMANCE_THRESHOLDS.MODERATE) {
      // Performances moyennes : réduire la durée
      return {
        ...baseTransition,
        duration: baseTransition.duration * 0.75
      };
    }
    
    return baseTransition;
  },
  
  // Créer des variants avec support de reduced motion
  createAccessibleVariants: (variants) => {
    if (ANIMATION_UTILS.shouldReduceMotion()) {
      return {
        initial: variants.animate || {},
        animate: variants.animate || {},
        exit: variants.animate || {}
      };
    }
    return variants;
  }
};