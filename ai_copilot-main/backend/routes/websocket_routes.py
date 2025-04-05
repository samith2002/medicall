from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
import logging
import json
from typing import Dict, Any

from services.call_service import call_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])

@router.websocket("/ws/call/{call_id}")
async def websocket_endpoint(websocket: WebSocket, call_id: str):
    """WebSocket endpoint for real-time call updates"""
    await websocket.accept()
    
    # Send initial message
    await websocket.send_json({"type": "connected", "call_id": call_id})
    
    # Register websocket connection
    call_service.register_websocket(call_id, websocket)
    
    try:
        # Send call history if available
        call_info = call_service.get_call_info(call_id)
        if call_info:
            # Send transcript history
            for transcript in call_info.transcript_history:
                await websocket.send_json({
                    "type": "transcript",
                    "call_id": call_id,
                    "text": transcript.text,
                    "is_final": transcript.is_final,
                    "timestamp": transcript.timestamp
                })
            
            # Send response history
            for response in call_info.response_history:
                await websocket.send_json({
                    "type": "response",
                    "call_id": call_id,
                    "text": response.text,
                    "model": response.model,
                    "timestamp": response.timestamp
                })
        
        # Keep connection alive and handle client messages
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # Handle client messages (e.g., frontend confirmations)
                await websocket.send_json({"type": "ack", "data": message})
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for call: {call_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        # Unregister websocket connection
        call_service.unregister_websocket(call_id, websocket)
        
@router.websocket("/ws/monitor")
async def monitor_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for monitoring all calls (admin use)"""
    await websocket.accept()
    
    # This is a special websocket that receives updates for all calls
    # It's useful for admin panels or monitoring dashboards
    
    try:
        # Keep connection alive and monitor all call events
        while True:
            # For now, we just keep the connection alive
            # In the future, we could broadcast all call events here
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                
                # Process admin commands
                if message.get("type") == "get_active_calls":
                    await websocket.send_json({
                        "type": "active_calls",
                        "calls": call_service.get_active_calls()
                    })
                else:
                    await websocket.send_json({"type": "ack", "data": message})
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
            
    except WebSocketDisconnect:
        logger.info("Admin monitor WebSocket disconnected")
    except Exception as e:
        logger.error(f"Admin WebSocket error: {str(e)}")
        # No need to unregister as this isn't associated with a specific call 

@router.websocket("/ws/live-audio/{call_id}")
async def live_audio_websocket(websocket: WebSocket, call_id: str):
    """WebSocket endpoint for real-time audio streaming and transcription"""
    await websocket.accept()
    
    # Send initial message
    await websocket.send_json({"type": "connected", "call_id": call_id, "message": "Live audio connection established"})
    
    # Register call if it doesn't exist
    if call_id not in call_service.get_active_calls():
        call_service.register_call(call_id, {"status": "active"})
    
    # Register websocket connection
    call_service.register_websocket(call_id, websocket)
    
    try:
        # Keep connection alive and handle audio chunks
        while True:
            # Receive binary audio data
            audio_data = await websocket.receive_bytes()
            
            # Process audio with Groq (in a non-blocking way)
            import asyncio
            from services.groq_service import groq_service
            
            # Convert bytes to base64 for processing
            import base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Process audio chunk (non-blocking)
            asyncio.create_task(process_live_audio(
                call_id=call_id,
                audio_data={"base64": audio_base64}
            ))
            
            # Send acknowledgment
            await websocket.send_json({"type": "audio_received", "size": len(audio_data)})
            
    except Exception as e:
        logger.error(f"WebSocket audio error: {str(e)}")
    finally:
        # Unregister websocket connection
        call_service.unregister_websocket(call_id, websocket)

async def process_live_audio(call_id: str, audio_data: Dict[str, Any]) -> None:
    """Process audio chunk and broadcast transcript"""
    try:
        from services.groq_service import groq_service
        
        # Transcribe audio using Groq
        transcribed_text = await groq_service.transcribe_audio(audio_data)
        
        if transcribed_text and transcribed_text.strip():
            # Broadcast transcript to connected clients
            await call_service.broadcast_transcript(call_id, transcribed_text, True)
            
            # Process transcript with Groq LLM for response generation
            from config import LLM_CONFIG
            response = await groq_service.generate_response(transcribed_text)
            
            if response:
                # Broadcast response to connected clients
                await call_service.broadcast_response(
                    call_id, 
                    response, 
                    LLM_CONFIG["model"]
                )
    
    except Exception as e:
        logger.error(f"Error processing live audio: {str(e)}") 