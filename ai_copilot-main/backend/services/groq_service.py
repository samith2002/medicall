import os
import base64
import tempfile
import logging
import time
from typing import Dict, Any, Optional, BinaryIO
from groq import Groq
from config import STT_CONFIG, LLM_CONFIG

logger = logging.getLogger(__name__)

class GroqService:
    """Service for handling interactions with Groq API"""
    
    def __init__(self):
        """Initialize the Groq client"""
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY environment variable not set")
        self.client = Groq(api_key=self.api_key)
    
    async def transcribe_audio(self, audio_data: Dict[str, Any]) -> Optional[str]:
        """Transcribe audio data using Groq's speech-to-text API"""
        try:
            audio_base64 = audio_data.get("base64", "")
            if not audio_base64:
                logger.error("No audio data received")
                return None
            
            # Decode audio and save to a temporary file
            audio_bytes = base64.b64decode(audio_base64)
            
            # Create a temporary file with the correct extension (.wav)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_audio_path = temp_file.name
                temp_file.write(audio_bytes)
            
            try:
                # Use Groq's speech-to-text API for transcription
                with open(temp_audio_path, "rb") as audio_file:
                    # Create a transcription using Groq's API
                    transcription = self.client.audio.transcriptions.create(
                        file=audio_file,
                        model=STT_CONFIG["model"],
                        language=STT_CONFIG["language"],
                        response_format=STT_CONFIG["response_format"]
                    )
                    
                    # Extract transcription text
                    transcribed_text = transcription.text if hasattr(transcription, 'text') else str(transcription)
                    
                    if transcribed_text:
                        logger.info(f"Transcription: {transcribed_text}")
                        return transcribed_text
                    else:
                        logger.warning("Empty transcription received")
                        return None
            
            except Exception as e:
                logger.error(f"Transcription error: {str(e)}")
                return None
            
            finally:
                # Clean up temp file
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
            
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            return None
    
    async def transcribe_audio_file(self, audio_file: BinaryIO) -> Optional[str]:
        """Transcribe an audio file using Groq's speech-to-text API"""
        try:
            # Create a transcription using Groq's API
            transcription = self.client.audio.transcriptions.create(
                file=audio_file,
                model=STT_CONFIG["model"],
                language=STT_CONFIG["language"],
                response_format=STT_CONFIG["response_format"]
            )
            
            # Extract transcription text
            transcribed_text = transcription.text if hasattr(transcription, 'text') else str(transcription)
            
            if transcribed_text:
                logger.info(f"Transcription: {transcribed_text}")
                return transcribed_text
            else:
                logger.warning("Empty transcription received")
                return None
        
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            return None
    
    async def generate_response(self, text: str) -> Optional[str]:
        """Generate a response using Groq's LLM API"""
        try:
            # Send the transcript to Groq for processing
            response = self.client.chat.completions.create(
                model=LLM_CONFIG["model"],
                messages=[
                    {"role": "system", "content": LLM_CONFIG["system_prompt"]},
                    {"role": "user", "content": text}
                ],
                temperature=LLM_CONFIG["temperature"],
                max_tokens=LLM_CONFIG["max_tokens"]
            )
            
            # Extract the response text
            assistant_response = response.choices[0].message.content
            logger.info(f"Groq response: {assistant_response}")
            return assistant_response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return None

# Create a singleton instance
groq_service = GroqService() 