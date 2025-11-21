import { useEffect, useRef } from 'react';
import '../styles/space-background.css';

const SpaceBackground = () => {
  const canvasRef = useRef(null);
  const starsRef = useRef([]);
  const planetsRef = useRef([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = window.innerWidth;
    const height = window.innerHeight;

    canvas.width = width;
    canvas.height = height;

    // Initialize stars
    if (starsRef.current.length === 0) {
      for (let i = 0; i < 100; i++) {
        starsRef.current.push({
          x: Math.random() * width,
          y: Math.random() * height,
          radius: Math.random() * 1.5,
          opacity: Math.random() * 0.5 + 0.5,
          twinkleDuration: Math.random() * 3000 + 1000,
          twinkling: 0,
        });
      }
    }

    // Initialize planets
    if (planetsRef.current.length === 0) {
      const colors = ['#3b82f6', '#ef4444', '#8b5cf6', '#f59e0b', '#10b981'];
      for (let i = 0; i < 5; i++) {
        planetsRef.current.push({
          x: Math.random() * width,
          y: Math.random() * height * 0.3,
          radius: Math.random() * 20 + 10,
          color: colors[i],
          vx: Math.random() * 0.5 - 0.25,
          vy: Math.random() * 0.3 - 0.15,
          opacity: 0.6,
        });
      }
    }

    let animationId;
    const startTime = Date.now();

    const animate = () => {
      // Clear canvas
      ctx.fillStyle = 'rgba(15, 23, 42, 0.1)';
      ctx.fillRect(0, 0, width, height);

      // Draw and update stars
      starsRef.current.forEach((star) => {
        const elapsed = (Date.now() - startTime) % star.twinkleDuration;
        const progress = elapsed / star.twinkleDuration;
        star.opacity = Math.abs(Math.sin(progress * Math.PI)) * 0.7 + 0.3;

        ctx.fillStyle = `rgba(243, 244, 246, ${star.opacity})`;
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
        ctx.fill();
      });

      // Draw and update planets
      planetsRef.current.forEach((planet) => {
        planet.x += planet.vx;
        planet.y += planet.vy;

        // Wrap around screen
        if (planet.x - planet.radius > width) planet.x = -planet.radius;
        if (planet.x + planet.radius < 0) planet.x = width + planet.radius;
        if (planet.y - planet.radius > height) planet.y = -planet.radius;
        if (planet.y + planet.radius < 0) planet.y = height + planet.radius;

        ctx.fillStyle = planet.color;
        ctx.globalAlpha = planet.opacity;
        ctx.beginPath();
        ctx.arc(planet.x, planet.y, planet.radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1;
      });

      animationId = requestAnimationFrame(animate);
    };

    animate();

    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return <canvas ref={canvasRef} className="space-background-canvas" />;
};

export default SpaceBackground;
