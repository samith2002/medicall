import React from 'react';

function Footer() {
  return (
    <footer className="bg-gray-800 py-4 px-6 text-center text-gray-400">
      <p>&copy; {new Date().getFullYear()} MediCall. All rights reserved.</p>
    </footer>
  );
}

export default Footer;