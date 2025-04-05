import os
import logging
from vapi_python import Vapi
from config import VAPI_CONFIG, WEBHOOK_CONFIG
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class VapiService:
    """Service for handling interactions with Vapi API"""
    
    def __init__(self):
        """Initialize the Vapi client"""
        self.api_key = os.getenv("VAPI_API_KEY")
        if not self.api_key:
            logger.warning("VAPI_API_KEY environment variable not set")
        self.client = Vapi(api_key=self.api_key)
    
    def create_assistant_config(self) -> Dict[str, Any]:
        """Create configuration for Vapi assistant"""
        return {
            "firstMessage": VAPI_CONFIG["first_message"],
            "context": VAPI_CONFIG["context"],
            "model": VAPI_CONFIG["model"],
            "voice": VAPI_CONFIG["voice"],
            "recordingEnabled": VAPI_CONFIG["recording_enabled"],
            "interruptionsEnabled": VAPI_CONFIG["interruptions_enabled"],
            "endCallOnSilence": VAPI_CONFIG["end_call_on_silence"],
            "silenceTimeoutSeconds": VAPI_CONFIG["silence_timeout_seconds"],
            "webhook": WEBHOOK_CONFIG,
            "rawAudio": VAPI_CONFIG["raw_audio"]
        }
    
    def start_call(self, assistant_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Start a call with Vapi"""
        if assistant_config is None:
            assistant_config = self.create_assistant_config()
        
        try:
            call = self.client.start(assistant=assistant_config)
            logger.info(f"Started call with ID: {call.get('call_id')}")
            return call
        except Exception as e:
            logger.error(f"Error starting call: {str(e)}")
            raise
    
    def stop_call(self) -> None:
        """Stop the active call"""
        try:
            self.client.stop()
            logger.info("Stopped active call")
        except Exception as e:
            logger.error(f"Error stopping call: {str(e)}")
            raise
    
    def send_message(self, message: str) -> None:
        """Send a message to the active call"""
        try:
            # Note: This is a placeholder as the actual implementation
            # depends on Vapi's API for sending messages to active calls
            logger.info(f"Sending message to active call: {message}")
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise

# Create a singleton instance
vapi_service = VapiService() 