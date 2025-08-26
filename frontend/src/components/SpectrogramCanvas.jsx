import React, { useRef, useEffect } from 'react';
import useJarvisStore from '../lib/store';

const SpectrogramCanvas = ({ isRecording, isProcessing }) => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const barsRef = useRef([]);
  const { settings } = useJarvisStore();

  const barCount = 16;
  const maxHeight = 40;

  // Initialize bars
  useEffect(() => {
    if (!barsRef.current.length) {
      barsRef.current = Array.from({ length: barCount }, () => ({
        height: 0,
        targetHeight: 0,
        velocity: 0
      }));
    }
  }, []);

  // Animation loop
  useEffect(() => {
    if (!canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    const animate = () => {
      // Clear canvas
      ctx.clearRect(0, 0, rect.width, rect.height);

      // Update bars
      barsRef.current.forEach((bar, index) => {
        if (isRecording || isProcessing) {
          // Generate random target heights with some patterns
          const baseIntensity = isProcessing ? 0.3 : 0.7;
          const randomness = Math.random() * baseIntensity;
          const waveEffect = Math.sin(Date.now() * 0.01 + index * 0.5) * 0.2;
          bar.targetHeight = (randomness + Math.abs(waveEffect)) * maxHeight;
        } else {
          bar.targetHeight = 0;
        }

        // Smooth animation using velocity
        const diff = bar.targetHeight - bar.height;
        bar.velocity += diff * 0.1;
        bar.velocity *= 0.8; // Damping
        bar.height += bar.velocity;

        // Clamp values
        bar.height = Math.max(0, Math.min(maxHeight, bar.height));
      });

      // Draw bars
      const barWidth = rect.width / barCount;
      const spacing = barWidth * 0.2;
      const actualBarWidth = barWidth - spacing;

      barsRef.current.forEach((bar, index) => {
        const x = index * barWidth + spacing / 2;
        const height = Math.max(2, bar.height);
        const y = rect.height - height;

        // Create gradient based on height
        const gradient = ctx.createLinearGradient(0, y, 0, rect.height);
        
        if (isProcessing) {
          gradient.addColorStop(0, '#ffb300'); // Warning color for processing
          gradient.addColorStop(1, '#ffb300');
        } else {
          const intensity = height / maxHeight;
          gradient.addColorStop(0, `rgba(0, 229, 255, ${intensity * 0.8})`); // Primary
          gradient.addColorStop(0.5, `rgba(109, 246, 255, ${intensity * 0.9})`); // Info
          gradient.addColorStop(1, `rgba(0, 229, 255, ${intensity})`);
        }

        ctx.fillStyle = gradient;
        ctx.fillRect(x, y, actualBarWidth, height);

        // Add glow effect for higher bars
        if (height > maxHeight * 0.5 && !settings.reducedMotion) {
          ctx.shadowBlur = 10;
          ctx.shadowColor = isProcessing ? '#ffb300' : '#00e5ff';
          ctx.fillRect(x, y, actualBarWidth, height);
          ctx.shadowBlur = 0;
        }
      });

      animationRef.current = requestAnimationFrame(animate);
    };

    // Start animation only if effects are enabled
    if (!settings.reducedMotion) {
      animate();
    } else {
      // Static visualization for reduced motion
      ctx.fillStyle = isProcessing ? '#ffb300' : '#00e5ff';
      const staticHeight = 8;
      barsRef.current.forEach((_, index) => {
        const x = index * (rect.width / barCount) + spacing / 2;
        const y = rect.height - staticHeight;
        ctx.fillRect(x, y, actualBarWidth, staticHeight);
      });
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isRecording, isProcessing, settings.reducedMotion]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  return (
    <div className="relative w-full h-full">
      <canvas
        ref={canvasRef}
        className="w-full h-full"
        style={{ 
          background: 'transparent',
          filter: settings.reducedMotion ? 'none' : 'drop-shadow(0 0 8px rgba(0, 229, 255, 0.3))'
        }}
      />
      
      {/* Background glow */}
      {!settings.reducedMotion && (isRecording || isProcessing) && (
        <div 
          className="absolute inset-0 rounded-lg opacity-20 animate-pulse-slow"
          style={{
            background: `radial-gradient(ellipse at center, ${
              isProcessing ? '#ffb300' : '#00e5ff'
            } 0%, transparent 70%)`,
          }}
        />
      )}
    </div>
  );
};

export default SpectrogramCanvas;