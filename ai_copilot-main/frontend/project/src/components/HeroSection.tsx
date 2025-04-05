import React from 'react';
import AnimatedBackground from './AnimatedBackground';
import ActionButtons from './ActionButtons';
import TalkToVAPIButton from './TalkToVAPIButton';

function HeroSection() {
  return (
    <div className="relative min-h-[calc(100vh-4rem)] flex items-center justify-center overflow-hidden">
      <AnimatedBackground />
      <div className="relative z-10 flex flex-col items-center text-center px-4">
        <h1 className="text-4xl md:text-6xl font-bold mb-6">
          Voice AI for the Modern Web
        </h1>
        <p className="text-xl md:text-2xl mb-12 max-w-2xl text-gray-300">
          Transform your web applications with powerful voice interactions
        </p>
        <ActionButtons />
        <TalkToVAPIButton />
      </div>
    </div>
  );
}

export default HeroSection;