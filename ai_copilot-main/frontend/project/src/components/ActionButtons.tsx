import React from 'react';
import { ArrowRight } from 'lucide-react';

function ActionButtons() {
  return (
    <div className="flex flex-col sm:flex-row gap-4 mb-8">
      <button className="bg-green-400 hover:bg-green-500 text-black font-bold py-2 px-6 rounded-full flex items-center justify-center">
        CONTACT SALES
        <ArrowRight className="ml-2 w-4 h-4" />
      </button>
      <button className="bg-transparent hover:bg-gray-700 text-white py-2 px-6 rounded-full border border-white flex items-center justify-center group">
        SIGN UP
        <span className="ml-2 flex space-x-1">
          <span className="animate-bounce delay-100">.</span>
          <span className="animate-bounce delay-200">.</span>
          <span className="animate-bounce delay-300">.</span>
        </span>
      </button>
    </div>
  );
}

export default ActionButtons;