import React, { useRef, useEffect } from 'react';
import useJarvisStore from '../lib/store';

const GridIsometricCanvas = () => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const { settings } = useJarvisStore();

  useEffect(() => {
    if (!canvasRef.current || settings.performanceMode) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    let animationOffset = 0;
    
    // Set canvas size
    const resizeCanvas = () => {
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * window.devicePixelRatio;
      canvas.height = rect.height * window.devicePixelRatio;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    };
    
    resizeCanvas();

    // Grid parameters
    const gridSize = window.innerWidth < 768 ? 40 : 30;
    const perspectiveAngle = 0.5;
    const baseOpacity = 0.1;

    // Draw isometric grid
    const drawGrid = () => {
      const width = canvas.width / window.devicePixelRatio;
      const height = canvas.height / window.devicePixelRatio;
      
      ctx.clearRect(0, 0, width, height);
      ctx.strokeStyle = `rgba(0, 229, 255, ${baseOpacity})`;
      ctx.lineWidth = 0.5;

      // Animated offset for movement effect
      if (!settings.reducedMotion) {
        animationOffset += 0.3;
      }
      
      const offsetX = (animationOffset % gridSize);
      const offsetY = (animationOffset * perspectiveAngle % gridSize);

      // Vertical lines (transformed for isometric effect)
      for (let x = -gridSize + offsetX; x < width + gridSize; x += gridSize) {
        const startX = x;
        const endX = x + height * perspectiveAngle;
        const startY = 0;
        const endY = height;
        
        // Fade lines based on distance from edges
        const distanceFromCenter = Math.abs((startX + endX) / 2 - width / 2);
        const fadeOpacity = Math.max(0, 1 - (distanceFromCenter / (width / 2))) * baseOpacity;
        
        ctx.strokeStyle = `rgba(0, 229, 255, ${fadeOpacity})`;
        
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.lineTo(endX, endY);
        ctx.stroke();
      }

      // Horizontal lines  
      for (let y = -gridSize + offsetY; y < height + gridSize; y += gridSize) {
        const startX = 0;
        const endX = width;
        const startY = y;
        const endY = y;
        
        // Fade lines based on distance from center
        const distanceFromCenter = Math.abs(y - height / 2);
        const fadeOpacity = Math.max(0, 1 - (distanceFromCenter / (height / 2))) * baseOpacity;
        
        ctx.strokeStyle = `rgba(0, 229, 255, ${fadeOpacity})`;
        
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.lineTo(endX, endY);
        ctx.stroke();
      }

      // Add some accent lines with glow effect
      if (!settings.performanceMode) {
        ctx.strokeStyle = `rgba(255, 59, 212, ${baseOpacity * 2})`;
        ctx.lineWidth = 1;
        ctx.shadowBlur = 10;
        ctx.shadowColor = 'rgba(255, 59, 212, 0.3)';
        
        // Draw a few accent lines
        for (let i = 0; i < 3; i++) {
          const x = (width / 4) * (i + 1) + Math.sin(animationOffset * 0.01 + i) * 20;
          ctx.beginPath();
          ctx.moveTo(x, 0);
          ctx.lineTo(x + height * perspectiveAngle, height);
          ctx.stroke();
        }
        
        ctx.shadowBlur = 0;
      }
    };

    // Animation loop
    const animate = () => {
      drawGrid();
      animationRef.current = requestAnimationFrame(animate);
    };

    // Start animation if not in reduced motion mode
    if (!settings.reducedMotion) {
      animate();
    } else {
      // Static grid for reduced motion
      drawGrid();
    }

    // Handle resize
    const handleResize = () => {
      resizeCanvas();
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
        opacity: settings.reducedMotion ? 0.2 : 0.4,
        mixBlendMode: 'screen',
      }}
    />
  );
};

export default GridIsometricCanvas;