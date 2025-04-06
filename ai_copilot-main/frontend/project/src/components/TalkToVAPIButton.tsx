import { useState, useEffect, useRef } from 'react';
import { Mic } from 'lucide-react';
import Vapi from "@vapi-ai/web";

interface TalkToVAPIButtonProps {
  onCallStateChange: (isActive: boolean) => void;
}


function TalkToVAPIButton({ onCallStateChange }: TalkToVAPIButtonProps) {
  const [isListening, setIsListening] = useState(false);
  const [microphonePermission, setMicrophonePermission] = useState<boolean | null>(null);
  const vapiInstanceRef = useRef<Vapi | null>(null);

  useEffect(() => {
    onCallStateChange(isListening);
  }, [isListening, onCallStateChange]);


  useEffect(() => {
    const checkMicrophonePermission = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        stream.getTracks().forEach(track => track.stop());
        setMicrophonePermission(true);
      } catch (error) {
        console.error("Microphone permission denied:", error);
        setMicrophonePermission(false);
      }
    };

    checkMicrophonePermission();

    return () => {
      if (vapiInstanceRef.current) {
        vapiInstanceRef.current.stop();
        vapiInstanceRef.current = null;
      }
    };
  }, []);

  const handleTalkToVAPI = async () => {
    if (!microphonePermission) {
      alert("Microphone permission is required to use this feature.");
      return;
    }

    if (isListening) {
      if (vapiInstanceRef.current) {
        vapiInstanceRef.current.stop();
        setIsListening(false);
        vapiInstanceRef.current = null;
      }
      return;
    }

    try {
      if (!vapiInstanceRef.current) {
        vapiInstanceRef.current = new Vapi(
          import.meta.env.VITE_VAPI_KEY || ""
        );

        vapiInstanceRef.current.on("call-start", () => {
          setIsListening(true);
        });

        vapiInstanceRef.current.on("call-end", () => {
          setIsListening(false);
          vapiInstanceRef.current = null;
        });

        vapiInstanceRef.current.on("error", (error) => {
          console.error("Vapi error:", error);
          setIsListening(false);
          alert("An error occurred during the call.");
          vapiInstanceRef.current?.stop();
          vapiInstanceRef.current = null;
        });
      }

      const assistantId = "a8e87a13-cb42-438e-8ecc-9de4ca9dd6f2";
    

      await vapiInstanceRef.current.start(assistantId);
    } catch (error) {
      console.error("Error starting Vapi call:", error);
      alert("Failed to start call. Please try again.");
      if (vapiInstanceRef.current) {
        vapiInstanceRef.current.stop();
        vapiInstanceRef.current = null;
      }
      setIsListening(false);
    }
  };

  return (
    <div className="text-center">
      <button
        className={`py-4 px-8 rounded-full border-2 font-bold flex items-center justify-center transition-all duration-300
          ${isListening 
            ? 'bg-[#28a745] border-[#28a745] text-white' 
            : 'bg-gray-400 border-gray-400 text-white hover:bg-gray-500 hover:border-gray-500'}`}
        onClick={handleTalkToVAPI}
        disabled={microphonePermission === null || microphonePermission === false}
      >
        <Mic className="w-6 h-6 mr-2" />
        {isListening ? "END CALL" : "CALL VAPI"}
        {isListening && (
          <span className="ml-2 flex space-x-1">
            <span className="animate-bounce delay-100">.</span>
            <span className="animate-bounce delay-200">.</span>
            <span className="animate-bounce delay-300">.</span>
          </span>
        )}
      </button>
      {microphonePermission === false && (
        <p className="text-red-500 mt-2 text-sm">
          Microphone permission is required. Please enable it in your browser settings.
        </p>
      )}
    </div>
  );
}

export default TalkToVAPIButton;