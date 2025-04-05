import React from 'react';

function AnimatedBackground() {
  const numberOfBars = 50;
  const barColors = ['bg-white', 'bg-blue-400', 'bg-purple-400', 'bg-yellow-400', 'bg-teal-400', 'bg-orange-400', 'bg-gray-400', 'bg-green-400'];

  const generateBars = () => {
    const bars = [];
    for (let i = 0; i < numberOfBars; i++) {
      const height = Math.floor(Math.random() * 10) + 1;
      const color = barColors[Math.floor(Math.random() * barColors.length)];
      bars.push(
        <div
          key={i}
          className={`rounded-full w-2 ${color} animate-pulse`}
          style={{ 
            height: `${height}rem`, 
            animationDelay: `${Math.random()}s`,
            opacity: '0.6'
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