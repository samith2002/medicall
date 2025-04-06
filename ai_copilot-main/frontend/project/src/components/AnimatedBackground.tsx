import React from 'react';

interface AnimatedBackgroundProps {
  isActive: boolean;
}

function AnimatedBackground({ isActive }: AnimatedBackgroundProps) {
  const numberOfBars = 50;
  // Light pastel colors for the bouncing bars
  const barColors = [
    'bg-[#FFB6C1]', // Light pink
    'bg-[#98FB98]', // Light green
    'bg-[#FFF68F]', // Light yellow
    'bg-[#DDA0DD]', // Light violet
    'bg-[#FFA07A]'  // Light orange
  ];

  const generateBars = () => {
    const bars = [];
    for (let i = 0; i < numberOfBars; i++) {
      const height = Math.floor(Math.random() * 10) + 1;
      const color = barColors[Math.floor(Math.random() * barColors.length)];
      const delay = Math.random() * 2; // Random delay between 0-2s
      const duration = 1 + Math.random(); // Random duration between 1-2s
      
      bars.push(
        <div
          key={i}
          className={`rounded-full w-3 ${color} transition-all duration-500
            ${isActive ? 'animate-bounce opacity-60' : 'opacity-25'}
            shadow-[0_0_15px_rgba(255,255,255,0.3)]`}
          style={{ 
            height: `${height}rem`, 
            animationDelay: `${delay}s`,
            animationDuration: `${duration}s`,
            transform: isActive ? undefined : `translateY(${Math.random() * 20 - 10}px)`,
            filter: 'brightness(1.2) contrast(1.1)',
            mixBlendMode: 'lighten'
          }}
        ></div>
      );
    }
    return bars;
  };

  return (
    <div className="absolute inset-0 flex items-center justify-around p-4 overflow-hidden">
      {generateBars()}
    </div>
  );
}

export default React.memo(AnimatedBackground);