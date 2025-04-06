import { Mic } from 'lucide-react';

function Header() {
  return (
    <header className="bg-black py-4 px-6 shadow-lg border-b border-white/10">
      <div className="text-2xl font-bold flex items-center text-gray-400">
        <Mic className="w-6 h-6 mr-2" />
        MediCall
      </div>
    </header>
  );
}

export default Header;