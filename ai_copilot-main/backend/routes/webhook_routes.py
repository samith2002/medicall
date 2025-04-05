from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
import logging
from typing import Dict, Any

from services.call_service import call_service
from services.groq_service import groq_service
from config import LLM_CONFIG

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])

@router.post("")
async def webhook_handler(request: Request, background_tasks: BackgroundTasks) -> Dict[str, str]:
    """Handle webhooks from Vapi"""
    try:
        data = await request.json()
        logger.info(f"Received webhook event: {data.get('event')}")
        
        event_type = data.get("event")
        call_id = data.get("callId")
        
        if not call_id:
            logger.warning("Webhook event missing call ID")
            return {"status": "error", "message": "Missing call ID"}
        
        if event_type == "call.created":
            # A new call has been created
            logger.info(f"New call created: {call_id}")
            # We don't register the call here as it hasn't started yet
            return {"status": "success"}
            
        elif event_type == "call.started":
            # Call has started, initialize call handling
            logger.info(f"Call started: {call_id}")
            # Register the call if it wasn't registered yet
            if call_id not in call_service.get_active_calls():
                call_service.register_call(call_id, {"status": "active"})
            return {"status": "success"}
            
        elif event_type == "transcription":
            # Handle speech transcription from Vapi
            transcript = data.get("transcript", {})
            text = transcript.get("text", "")
            is_final = transcript.get("is_final", False)
            
            if text:
                # Broadcast transcript to all connected clients
                background_tasks.add_task(
                    call_service.broadcast_transcript, 
                    call_id, 
                    text, 
                    is_final
                )
                
                if is_final:
                    # Process final transcription with Groq
                    background_tasks.add_task(
                        process_transcript_and_broadcast,
                        call_id,
                        text
                    )
            
            return {"status": "success"}
        
        elif event_type == "audio":
            # Handle raw audio data
            audio_data = data.get("audio", {})
            if audio_data:
                # Process the raw audio with Groq's speech-to-text
                background_tasks.add_task(
                    process_audio_and_broadcast,
                    call_id,
                    audio_data
                )
            
            return {"status": "success"}
            
        elif event_type == "call.ended":
            # Call has ended, clean up resources
            logger.info(f"Call ended: {call_id}")
            # We keep the call registered but mark it as inactive
            # so that frontend clients can still access the transcript
            if call_id in call_service.get_active_calls():
                call_service.unregister_call(call_id)
            return {"status": "success"}
            
        # Default response for other events
        return {"status": "received"}
    
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        # Always return success to Vapi to avoid retries
        return {"status": "error", "message": str(e)}

async def process_audio_and_broadcast(call_id: str, audio_data: Dict[str, Any]) -> None:
    """Process audio and broadcast transcript and response"""
    try:
        # Transcribe audio using Groq
        transcribed_text = await groq_service.transcribe_audio(audio_data)
        
        if transcribed_text:
            # Broadcast transcript to connected clients
            await call_service.broadcast_transcript(call_id, transcribed_text, True)
            
            # Process transcript with Groq LLM
            await process_transcript_and_broadcast(call_id, transcribed_text)
    
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")

async def process_transcript_and_broadcast(call_id: str, text: str) -> None:
    """Process transcript with Groq LLM and broadcast response"""
    try:
        # Generate response using Groq LLM
        response = await groq_service.generate_response(text)
        
        if response:
            # Broadcast response to connected clients
            await call_service.broadcast_response(
                call_id, 
                response, 
                LLM_CONFIG["model"]
            )
    
    except Exception as e:
        logger.error(f"Error processing transcript: {str(e)}") 