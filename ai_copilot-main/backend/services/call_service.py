import logging
import time
from typing import Dict, List, Set, Any, Optional
from fastapi import WebSocket
from models.schemas import TranscriptMessage, ResponseMessage, CallInfo

logger = logging.getLogger(__name__)

class CallService:
    """Service for managing active calls and their data"""
    
    def __init__(self):
        """Initialize the call service"""
        # Active calls data store
        self.active_calls: Dict[str, Dict[str, Any]] = {}
        
        # WebSocket connections for each call
        self.websocket_connections: Dict[str, Set[WebSocket]] = {}
        
        # Call transcript history
        self.transcript_history: Dict[str, List[TranscriptMessage]] = {}
        
        # Call response history
        self.response_history: Dict[str, List[ResponseMessage]] = {}
    
    def register_call(self, call_id: str, call_data: Dict[str, Any]) -> None:
        """Register a new call"""
        self.active_calls[call_id] = call_data
        self.websocket_connections[call_id] = set()
        self.transcript_history[call_id] = []
        self.response_history[call_id] = []
        logger.info(f"Registered new call: {call_id}")
    
    def unregister_call(self, call_id: str) -> None:
        """Unregister a call"""
        if call_id in self.active_calls:
            del self.active_calls[call_id]
        
        # Close all websocket connections for this call
        if call_id in self.websocket_connections:
            for ws in self.websocket_connections[call_id]:
                try:
                    ws.close()
                except Exception as e:
                    logger.error(f"Error closing websocket: {str(e)}")
            del self.websocket_connections[call_id]
        
        # Keep transcript and response history for later retrieval
        logger.info(f"Unregistered call: {call_id}")
    
    def register_websocket(self, call_id: str, websocket: WebSocket) -> None:
        """Register a websocket connection for a call"""
        if call_id not in self.websocket_connections:
            self.websocket_connections[call_id] = set()
        self.websocket_connections[call_id].add(websocket)
        logger.info(f"Registered new websocket for call: {call_id}")
    
    def unregister_websocket(self, call_id: str, websocket: WebSocket) -> None:
        """Unregister a websocket connection for a call"""
        if call_id in self.websocket_connections:
            self.websocket_connections[call_id].discard(websocket)
            logger.info(f"Unregistered websocket for call: {call_id}")
    
    async def broadcast_transcript(self, call_id: str, text: str, is_final: bool = False) -> None:
        """Broadcast a transcript to all connected websockets for a call"""
        if call_id not in self.websocket_connections:
            return
        
        timestamp = time.time()
        
        # Store transcript in history
        transcript = TranscriptMessage(
            call_id=call_id,
            text=text,
            is_final=is_final,
            timestamp=timestamp
        )
        self.transcript_history[call_id].append(transcript)
        
        # Broadcast to all connected websockets
        message = {
            "type": "transcript",
            "call_id": call_id,
            "text": text,
            "is_final": is_final,
            "timestamp": timestamp
        }
        
        for ws in self.websocket_connections[call_id]:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.error(f"Error sending transcript to websocket: {str(e)}")
                # Don't remove it here, it will be handled in the websocket endpoint
    
    async def broadcast_response(self, call_id: str, text: str, model: str) -> None:
        """Broadcast a response to all connected websockets for a call"""
        if call_id not in self.websocket_connections:
            return
        
        timestamp = time.time()
        
        # Store response in history
        response = ResponseMessage(
            call_id=call_id,
            text=text,
            model=model,
            timestamp=timestamp
        )
        self.response_history[call_id].append(response)
        
        # Broadcast to all connected websockets
        message = {
            "type": "response",
            "call_id": call_id,
            "text": text,
            "model": model,
            "timestamp": timestamp
        }
        
        for ws in self.websocket_connections[call_id]:
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.error(f"Error sending response to websocket: {str(e)}")
    
    def get_call_info(self, call_id: str) -> Optional[CallInfo]:
        """Get information about a call"""
        if call_id not in self.transcript_history:
            return None
        
        status = "active" if call_id in self.active_calls else "ended"
        
        return CallInfo(
            call_id=call_id,
            status=status,
            transcript_history=self.transcript_history.get(call_id, []),
            response_history=self.response_history.get(call_id, [])
        )
    
    def get_active_calls(self) -> List[str]:
        """Get a list of active call IDs"""
        return list(self.active_calls.keys())
    
    def get_all_calls(self) -> List[str]:
        """Get a list of all call IDs (active and ended)"""
        return list(set(self.transcript_history.keys()))

# Create a singleton instance
call_service = CallService() 