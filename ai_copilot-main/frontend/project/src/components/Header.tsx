import React from 'react';
import { Mic } from 'lucide-react';

function Header() {
  return (
    <header className="bg-gray-900 py-4 px-6 flex items-center justify-between">
      <div className="text-xl font-bold flex items-center">
        <Mic className="w-6 h-6 mr-2" />
        VAPI
      </div>
      <nav className="hidden md:flex space-x-4">
        <a href="#" className="hover:text-gray-300">USE CASES</a>
        <a href="#" className="hover:text-gray-300">FEATURES</a>
        <a href="#" className="hover:text-gray-300">BLOG</a>
        <a href="#" className="hover:text-gray-300">CAREERS</a>
        <a href="#" className="hover:text-gray-300">STARTUPS</a>
        <a href="#" className="hover:text-gray-300">DOCS</a>
      </nav>
      <div>
        <button className="bg-transparent hover:bg-gray-700 text-white py-2 px-4 rounded-full border border-white">
          OPEN DASHBOARD
        </button>
      </div>
    </header>
  );
}

export default Header;