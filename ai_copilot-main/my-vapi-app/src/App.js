// src/App.js
import React from 'react';
import './App.css'; // Keep default styling or modify
import VapiComponent from './VapiComponent'; // Import your component

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Vapi React Test</h1>
      </header>
      <main>
        <VapiComponent /> {/* Use your component here */}
      </main>
    </div>
  );
}

export default App;