import React, { useRef, useEffect } from 'react';
import useJarvisStore from '../lib/store';

const ParticlesBackground = () => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const particlesRef = useRef([]);
  const { settings } = useJarvisStore();

  // Particle class
  class Particle {
    constructor(canvas) {
      this.canvas = canvas;
      this.reset();
      this.y = Math.random() * canvas.height;
      this.opacity = Math.random() * 0.5 + 0.2;
    }

    reset() {
      this.x = Math.random() * this.canvas.width;
      this.y = -10;
      this.size = Math.random() * 2 + 1;
      this.speedX = (Math.random() - 0.5) * 0.5;
      this.speedY = Math.random() * 0.5 + 0.2;
      this.opacity = Math.random() * 0.5 + 0.2;
      this.color = this.getRandomColor();
      this.pulsePhase = Math.random() * Math.PI * 2;
    }

    getRandomColor() {
      const colors = [
        'rgba(0, 229, 255, ',     // Primary
        'rgba(109, 246, 255, ',  // Info
        'rgba(255, 59, 212, ',   // Accent
        'rgba(76, 255, 122, ',   // Success
      ];
      return colors[Math.floor(Math.random() * colors.length)];
    }

    update() {
      this.x += this.speedX;
      this.y += this.speedY;
      
      // Pulse effect
      this.pulsePhase += 0.02;
      const pulse = Math.sin(this.pulsePhase) * 0.2 + 0.8;
      this.currentOpacity = this.opacity * pulse;

      // Reset if particle goes out of bounds
      if (this.y > this.canvas.height + 10 || 
          this.x < -10 || 
          this.x > this.canvas.width + 10) {
        this.reset();
      }
    }

    draw(ctx) {
      ctx.save();
      ctx.globalAlpha = this.currentOpacity || this.opacity;
      
      // Main particle
      ctx.fillStyle = this.color + (this.currentOpacity || this.opacity) + ')';
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fill();

      // Glow effect
      if (!settings.performanceMode) {
        ctx.shadowBlur = 20;
        ctx.shadowColor = this.color + '0.8)';
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size * 0.5, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.restore();
    }
  }

  // Initialize particles
  useEffect(() => {
    if (!canvasRef.current || settings.performanceMode) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    const resizeCanvas = () => {
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * window.devicePixelRatio;
      canvas.height = rect.height * window.devicePixelRatio;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    };
    
    resizeCanvas();
    
    // Determine particle count based on device
    const isMobile = window.innerWidth < 768;
    const particleCount = isMobile ? 15 : 30;
    
    // Create particles
    particlesRef.current = Array.from({ length: particleCount }, () => new Particle(canvas));

    // Animation loop
    const animate = () => {
      // Clear canvas with slight trail effect
      ctx.fillStyle = 'rgba(6, 8, 12, 0.1)';
      ctx.fillRect(0, 0, canvas.width / window.devicePixelRatio, canvas.height / window.devicePixelRatio);

      // Update and draw particles
      particlesRef.current.forEach(particle => {
        particle.update();
        particle.draw(ctx);
      });

      // Draw connections between nearby particles
      if (!settings.performanceMode && !isMobile) {
        drawConnections(ctx);
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    // Draw connections between particles
    const drawConnections = (ctx) => {
      const connectionDistance = 100;
      
      for (let i = 0; i < particlesRef.current.length; i++) {
        for (let j = i + 1; j < particlesRef.current.length; j++) {
          const dx = particlesRef.current[i].x - particlesRef.current[j].x;
          const dy = particlesRef.current[i].y - particlesRef.current[j].y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < connectionDistance) {
            const opacity = (1 - distance / connectionDistance) * 0.1;
            
            ctx.save();
            ctx.strokeStyle = `rgba(0, 229, 255, ${opacity})`;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(particlesRef.current[i].x, particlesRef.current[i].y);
            ctx.lineTo(particlesRef.current[j].x, particlesRef.current[j].y);
            ctx.stroke();
            ctx.restore();
          }
        }
      }
    };

    // Start animation if not in reduced motion mode
    if (!settings.reducedMotion) {
      animate();
    }

    // Handle resize
    const handleResize = () => {
      resizeCanvas();
      particlesRef.current.forEach(particle => {
        particle.canvas = canvas;
      });
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [settings.performanceMode, settings.reducedMotion]);

  // Don't render if performance mode is on
  if (settings.performanceMode) {
    return null;
  }

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 pointer-events-none z-0"
      style={{
        background: 'transparent',
        opacity: settings.reducedMotion ? 0.3 : 1,
      }}
    />
  );
};

export default ParticlesBackground;