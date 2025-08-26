import React, { useRef, useEffect } from 'react';
import useJarvisStore from '../lib/store';

const SpectrogramCanvas = ({ isRecording, isProcessing }) => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const barsRef = useRef([]);
  const { settings } = useJarvisStore();

  const barCount = 20;
  const maxHeight = 36;

  // Initialize bars
  useEffect(() => {
    if (!barsRef.current.length) {
      barsRef.current = Array.from({ length: barCount }, () => ({
        height: 0,
        targetHeight: 0,
        velocity: 0,
        frequency: Math.random() * 0.1 + 0.02, // Random frequency for each bar
        phase: Math.random() * Math.PI * 2 // Random phase offset
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

    let animationTime = 0;

    const animate = () => {
      animationTime += 0.016; // Roughly 60fps

      // Clear canvas with subtle trail effect
      ctx.fillStyle = 'rgba(6, 8, 12, 0.3)';
      ctx.fillRect(0, 0, rect.width, rect.height);

      // Update bars
      barsRef.current.forEach((bar, index) => {
        if (isRecording || isProcessing) {
          // Create wave patterns for more realistic audio visualization
          const baseIntensity = isProcessing ? 0.4 : 0.8;
          const waveIntensity = Math.sin(animationTime * bar.frequency + bar.phase) * 0.3;
          const randomness = Math.random() * 0.4;
          
          // Add some bass-like behavior to lower indices
          const bassBoost = index < barCount * 0.3 ? Math.sin(animationTime * 0.5) * 0.2 : 0;
          
          bar.targetHeight = Math.max(0.1, 
            (baseIntensity + Math.abs(waveIntensity) + randomness + Math.abs(bassBoost)) * maxHeight
          );
        } else {
          bar.targetHeight = 0;
        }

        // Smooth animation using velocity with enhanced physics
        const diff = bar.targetHeight - bar.height;
        bar.velocity += diff * 0.15; // Spring constant
        bar.velocity *= 0.85; // Damping factor
        bar.height += bar.velocity;

        // Clamp values
        bar.height = Math.max(0, Math.min(maxHeight, bar.height));
      });

      // Draw bars with enhanced cyber styling
      const barWidth = rect.width / barCount;
      const spacing = barWidth * 0.15;
      const actualBarWidth = barWidth - spacing;

      barsRef.current.forEach((bar, index) => {
        const x = index * barWidth + spacing / 2;
        const height = Math.max(1, bar.height);
        const y = rect.height - height;

        // Create dynamic gradient based on height and processing state
        const gradient = ctx.createLinearGradient(0, y, 0, rect.height);
        const intensity = height / maxHeight;
        
        if (isProcessing) {
          // Orange processing colors
          gradient.addColorStop(0, `rgba(255, 179, 0, ${intensity * 0.9})`);
          gradient.addColorStop(0.5, `rgba(255, 179, 0, ${intensity * 0.7})`);
          gradient.addColorStop(1, `rgba(255, 179, 0, ${intensity * 0.9})`);
        } else {
          // Cyan to purple cyber gradient
          const baseAlpha = intensity * 0.8;
          gradient.addColorStop(0, `rgba(0, 229, 255, ${baseAlpha})`);
          gradient.addColorStop(0.3, `rgba(109, 246, 255, ${baseAlpha * 0.8})`);
          gradient.addColorStop(0.6, `rgba(138, 43, 226, ${baseAlpha * 0.6})`);
          gradient.addColorStop(1, `rgba(255, 59, 212, ${baseAlpha * 0.4})`);
        }

        // Draw main bar
        ctx.fillStyle = gradient;
        ctx.fillRect(x, y, actualBarWidth, height);

        // Add cyber glow effect for taller bars
        if (height > maxHeight * 0.4 && !settings.reducedMotion) {
          const glowColor = isProcessing ? '#ffb300' : '#00e5ff';
          const glowIntensity = (height / maxHeight) * 0.5;
          
          ctx.shadowBlur = 15;
          ctx.shadowColor = glowColor;
          ctx.globalAlpha = glowIntensity;
          ctx.fillRect(x, y, actualBarWidth, height);
          ctx.shadowBlur = 0;
          ctx.globalAlpha = 1;
          
          // Add inner highlight
          const highlightGradient = ctx.createLinearGradient(0, y, 0, y + height * 0.3);
          highlightGradient.addColorStop(0, `rgba(255, 255, 255, ${glowIntensity * 0.3})`);
          highlightGradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
          ctx.fillStyle = highlightGradient;
          ctx.fillRect(x, y, actualBarWidth, height * 0.3);
        }

        // Add subtle cyber grid lines
        if (index % 4 === 0) {
          ctx.strokeStyle = isProcessing 
            ? 'rgba(255, 179, 0, 0.1)' 
            : 'rgba(0, 229, 255, 0.1)';
          ctx.lineWidth = 0.5;
          ctx.beginPath();
          ctx.moveTo(x, 0);
          ctx.lineTo(x, rect.height);
          ctx.stroke();
        }
      });

      // Add scanning line effect
      if (!settings.reducedMotion && (isRecording || isProcessing)) {
        const scanX = (animationTime * 50) % (rect.width + 20) - 10;
        const scanGradient = ctx.createLinearGradient(scanX - 10, 0, scanX + 10, 0);
        const scanColor = isProcessing ? '255, 179, 0' : '0, 229, 255';
        
        scanGradient.addColorStop(0, `rgba(${scanColor}, 0)`);
        scanGradient.addColorStop(0.5, `rgba(${scanColor}, 0.6)`);
        scanGradient.addColorStop(1, `rgba(${scanColor}, 0)`);
        
        ctx.fillStyle = scanGradient;
        ctx.fillRect(scanX - 10, 0, 20, rect.height);
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    // Start animation if not in reduced motion mode
    if (!settings.reducedMotion) {
      animate();
    } else {
      // Static visualization for reduced motion
      const staticColor = isProcessing ? '#ffb300' : '#00e5ff';
      ctx.fillStyle = staticColor;
      const staticHeight = 12;
      
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
    <div className="relative w-full h-full rounded-lg overflow-hidden">
      <canvas
        ref={canvasRef}
        className="w-full h-full"
        style={{ 
          background: 'transparent',
          filter: settings.reducedMotion ? 'none' : 'drop-shadow(0 0 8px rgba(0, 229, 255, 0.3))'
        }}
      />
      
      {/* Background cyber grid */}
      {!settings.reducedMotion && (isRecording || isProcessing) && (
        <div 
          className="absolute inset-0 rounded-lg opacity-20"
          style={{
            background: `
              radial-gradient(circle at 30% 30%, ${
                isProcessing ? '#ffb300' : '#00e5ff'
              } 0%, transparent 50%),
              radial-gradient(circle at 70% 70%, ${
                isProcessing ? '#ff3bd4' : '#8a2be2'
              } 0%, transparent 50%)
            `,
            backgroundSize: '100% 100%',
            animation: 'neonPulseCyan 3s ease-in-out infinite alternate'
          }}
        />
      )}
      
      {/* Cyber frame border */}
      <div className={`absolute inset-0 rounded-lg border-2 ${
        isRecording 
          ? 'border-jarvis-neon-pink/30 shadow-neon-pink animate-neon-pulse-pink'
          : isProcessing 
            ? 'border-jarvis-neon-orange/30 shadow-neon-orange'
            : 'border-jarvis-neon-cyan/30 shadow-neon-cyan'
      } transition-all duration-300`} />
    </div>
  );
};

export default SpectrogramCanvas;