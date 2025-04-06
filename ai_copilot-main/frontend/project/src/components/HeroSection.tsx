import { useState } from 'react';
import AnimatedBackground from './AnimatedBackground';
import TalkToVAPIButton from './TalkToVAPIButton';

function HeroSection() {
  const [isCallActive, setIsCallActive] = useState(false);

  return (
    <div className="relative min-h-[calc(100vh-4rem)] flex items-center justify-center overflow-hidden">
      <AnimatedBackground isActive={isCallActive} />
      <div className="relative z-10 flex flex-col items-center justify-center text-center px-4 max-w-4xl mx-auto h-full">
        <div className="space-y-20">
          <div>
            <h1 className="text-5xl md:text-7xl font-bold text-gray-400 mb-6">
              MediCall
            </h1>
            <div className="space-y-2">
              <p className="text-xl md:text-2xl font-medium text-white/90 leading-relaxed drop-shadow">
                Schedule medical appointments effortlessly using your voice.
              </p>
              <p className="text-xl md:text-2xl font-medium text-white/90 leading-relaxed drop-shadow">
                Simply tap the button and speak!
              </p>
            </div>
          </div>
          <div className="flex justify-center items-center">
            <TalkToVAPIButton onCallStateChange={setIsCallActive} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default HeroSection;