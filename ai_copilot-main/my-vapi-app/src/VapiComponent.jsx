import React, { useState, useEffect, useRef } from 'react';
import Vapi from '@vapi-ai/web';

// --- Configuration ---
// Replace with your actual Public API Key from Vapi Dashboard
const VAPI_PUBLIC_KEY = 'YOUR_VAPI_PUBLIC_KEY';
// Replace with your actual Assistant ID from Vapi Dashboard
const VAPI_ASSISTANT_ID = 'YOUR_ASSISTANT_ID';
// ---------------------

const VapiComponent = () => {
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [callStatus, setCallStatus] = useState('idle'); // idle, connecting, connected, ending, ended, error
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState(null);
  const vapiRef = useRef(null); // Using ref to hold the Vapi instance

  // --- Initialize Vapi ---
  useEffect(() => {
    if (!VAPI_PUBLIC_KEY || VAPI_PUBLIC_KEY === 'YOUR_VAPI_PUBLIC_KEY') {
      setError('Error: Vapi Public Key not set. Please update VAPI_PUBLIC_KEY in the code.');
      setCallStatus('error');
      return;
    }
    // Create Vapi instance only once
    if (!vapiRef.current) {
      vapiRef.current = new Vapi(VAPI_PUBLIC_KEY);
    }

    const vapi = vapiRef.current;

    // --- Event Listeners ---
    const handleCallStart = () => {
      console.log('Vapi Call Started');
      setCallStatus('connected');
      setIsSessionActive(true);
      setTranscript(''); // Clear transcript on new call
      setError(null);
    };

    const handleCallEnd = () => {
      console.log('Vapi Call Ended');
      setCallStatus('ended');
      setIsSessionActive(false);
    };

    const handleMessage = (message) => {
      console.log('Vapi Message:', message);
      if (message.type === 'transcript' && message.transcriptType === 'final') {
        // Append final user transcript
        setTranscript((prev) => prev + `User: ${message.transcript}\n`);
      } else if (message.type === 'assistant-message') {
        // Append assistant message (assuming text content)
        if(message.message.type === 'text') {
          setTranscript((prev) => prev + `Assistant: ${message.message.text}\n`);
        }
      }
      // Add more conditions here to handle other message types if needed
      // (e.g., 'function-call', 'speech-update', etc.)
    };

    const handleError = (e) => {
      console.error('Vapi Error:', e);
      setCallStatus('error');
      setError(e?.message || 'An unknown Vapi error occurred.');
      setIsSessionActive(false);
    };

    // Register listeners
    vapi.on('call-start', handleCallStart);
    vapi.on('call-end', handleCallEnd);
    vapi.on('message', handleMessage);
    vapi.on('error', handleError);

    // --- Cleanup Function ---
    return () => {
      // Unregister listeners
      vapi.off('call-start', handleCallStart);
      vapi.off('call-end', handleCallEnd);
      vapi.off('message', handleMessage);
      vapi.off('error', handleError);

      // Optional: Stop call if component unmounts while active
      // Note: This might interfere if you want calls to persist across navigation
      // if (isSessionActive) {
      //   vapi.stop();
      // }
    };
    // Rerun effect only if VAPI_PUBLIC_KEY changes (which it shouldn't dynamically)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [VAPI_PUBLIC_KEY]);

  // --- Action Handlers ---
  const startCall = async () => {
    const vapi = vapiRef.current;
    if (!vapi) {
        setError("Vapi instance not initialized.");
        setCallStatus('error');
        return;
    }
     if (!VAPI_ASSISTANT_ID || VAPI_ASSISTANT_ID === 'YOUR_ASSISTANT_ID') {
      setError('Error: Vapi Assistant ID not set. Please update VAPI_ASSISTANT_ID in the code.');
      setCallStatus('error');
      return;
    }

    setCallStatus('connecting');
    setError(null);
    try {
      // Start the call using the configured Assistant ID
      await vapi.start(VAPI_ASSISTANT_ID);
      // Note: Actual status update to 'connected' is handled by the 'call-start' event listener
    } catch (e) {
      console.error('Failed to start Vapi call:', e);
      setError(e?.message || 'Failed to start the call.');
      setCallStatus('error');
      setIsSessionActive(false);
    }
  };

  const stopCall = () => {
     const vapi = vapiRef.current;
    if (!vapi) {
        console.warn("Attempted to stop call, but Vapi instance not available.");
        return;
    }
    setCallStatus('ending');
    vapi.stop();
    // Note: Actual status update to 'ended' is handled by the 'call-end' event listener
  };

  // --- Render ---
  return (
    <div style={styles.container}>
      <h2>Vapi.ai React Integration</h2>

      <div style={styles.controls}>
        <button
          onClick={startCall}
          disabled={isSessionActive || callStatus === 'connecting' || callStatus === 'error' && !error?.includes('set')}
          style={styles.button}
        >
          {callStatus === 'connecting' ? 'Connecting...' : 'Start Call'}
        </button>
        <button
          onClick={stopCall}
          disabled={!isSessionActive || callStatus === 'ending'}
          style={styles.button}
        >
           {callStatus === 'ending' ? 'Ending...' : 'End Call'}
        </button>
      </div>

      <div style={styles.status}>
        <strong>Status:</strong> {callStatus}
      </div>

      {error && (
        <div style={styles.error}>
          <strong>Error:</strong> {error}
        </div>
      )}

      <div style={styles.transcriptContainer}>
        <strong>Transcript:</strong>
        <pre style={styles.transcriptBox}>{transcript || '(Conversation will appear here...)'}</pre>
      </div>
    </div>
  );
};

// --- Basic Styling ---
const styles = {
  container: {
    fontFamily: 'sans-serif',
    padding: '20px',
    border: '1px solid #ccc',
    borderRadius: '8px',
    maxWidth: '600px',
    margin: '20px auto',
  },
  controls: {
    marginBottom: '15px',
    display: 'flex',
    gap: '10px',
  },
  button: {
    padding: '10px 15px',
    fontSize: '1rem',
    cursor: 'pointer',
    borderRadius: '5px',
    border: '1px solid #007bff',
    backgroundColor: '#007bff',
    color: 'white',
  },
  'button:disabled': { // Note: inline styles don't support pseudo-classes directly
                      // You might need CSS modules or styled-components for this.
                      // Or conditionally apply different styles.
    backgroundColor: '#cccccc',
    borderColor: '#999999',
    cursor: 'not-allowed',
  },
  status: {
    marginBottom: '10px',
    fontWeight: 'bold',
    padding: '8px',
    backgroundColor: '#f0f0f0',
    borderRadius: '4px',
  },
  error: {
    marginBottom: '10px',
    color: 'red',
    fontWeight: 'bold',
    padding: '8px',
    backgroundColor: '#ffe0e0',
    border: '1px solid red',
    borderRadius: '4px',
  },
  transcriptContainer: {
    marginTop: '15px',
  },
  transcriptBox: {
    marginTop: '5px',
    padding: '10px',
    border: '1px solid #eee',
    borderRadius: '4px',
    backgroundColor: '#f9f9f9',
    minHeight: '150px',
    maxHeight: '400px',
    overflowY: 'auto', // Make transcript scrollable
    whiteSpace: 'pre-wrap', // Preserve line breaks
    wordWrap: 'break-word', // Wrap long lines
    fontSize: '0.9rem',
    lineHeight: '1.4',
  }
};

export default VapiComponent;