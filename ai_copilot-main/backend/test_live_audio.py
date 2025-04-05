#!/usr/bin/env python3
"""
Test script for live audio transcription and response generation.
This script records audio from the microphone, sends it to the backend,
and prints the transcription and response.
"""

import asyncio
import websockets
import pyaudio
import os
import base64
import json
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default settings
CHUNK_SIZE = 4096  # Audio chunk size
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Mono audio
RATE = 16000  # Sample rate (16kHz is standard for STT)
API_URL = "ws://localhost:8000/ws/live-audio"  # Default WebSocket URL

async def stream_audio_to_backend(call_id, server_url=None):
    """Stream audio from the microphone to the backend"""
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    
    # Open microphone stream
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )
    
    print(f"Connecting to {server_url}/{call_id}...")
    
    try:
        # Connect to WebSocket
        async with websockets.connect(f"{server_url}/{call_id}") as websocket:
            print("Connected! Start speaking...")
            
            # Listen for incoming messages from the backend in the background
            async def receive_messages():
                while True:
                    try:
                        message = await websocket.recv()
                        # Try to parse as JSON
                        try:
                            data = json.loads(message)
                            if data.get("type") == "transcript":
                                print(f"\nTranscript: {data.get('text')}")
                            elif data.get("type") == "response":
                                print(f"\nResponse: {data.get('text')}")
                        except:
                            # Binary message or non-JSON
                            print(f"Received: {message[:30]}...")
                    except websockets.exceptions.ConnectionClosed:
                        print("Connection closed")
                        break
            
            # Start receiving messages in the background
            receive_task = asyncio.create_task(receive_messages())
            
            # Stream audio to the backend
            print("Recording... Press Ctrl+C to stop")
            try:
                while True:
                    # Read audio chunk
                    audio_data = stream.read(CHUNK_SIZE)
                    
                    # Send raw audio bytes
                    await websocket.send(audio_data)
                    
                    # Print a dot to show activity
                    print(".", end="", flush=True)
                    
                    # Small delay to prevent overwhelming the server
                    await asyncio.sleep(0.1)
            
            except KeyboardInterrupt:
                print("\nStopping...")
            
            finally:
                # Clean up
                receive_task.cancel()
                try:
                    await receive_task
                except asyncio.CancelledError:
                    pass
    
    except Exception as e:
        print(f"Error: {str(e)}")
    
    finally:
        # Stop and close the audio stream
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("Audio stream closed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test live audio transcription")
    parser.add_argument("--call-id", default="test-call-" + os.urandom(4).hex(), help="Call ID to use")
    parser.add_argument("--server", default=API_URL, help="Backend WebSocket URL")
    
    args = parser.parse_args()
    
    print(f"Testing live audio transcription with call ID: {args.call_id}")
    
    # Run the WebSocket client
    asyncio.run(stream_audio_to_backend(args.call_id, args.server)) 