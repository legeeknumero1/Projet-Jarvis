#!/usr/bin/env python3
"""
Audio Bridge WebSocket Server for Jarvis Interface
Handles audio streaming between frontend and backend containers
"""

import asyncio
import json
import logging
import websockets
from websockets.server import WebSocketServerProtocol
from typing import Dict, Set
import httpx
import wave
import io
import base64
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioBridge:
    def __init__(self):
        self.active_connections: Set[WebSocketServerProtocol] = set()
        self.audio_sessions: Dict[str, dict] = {}
        self.tts_client = httpx.AsyncClient()
        self.stt_client = httpx.AsyncClient()
        
    async def register_connection(self, websocket: WebSocketServerProtocol):
        """Register a new WebSocket connection"""
        self.active_connections.add(websocket)
        session_id = f"session_{len(self.active_connections)}_{datetime.now().timestamp()}"
        self.audio_sessions[session_id] = {
            'websocket': websocket,
            'state': 'idle',
            'audio_buffer': bytearray(),
            'created_at': datetime.now()
        }
        logger.info(f"New connection registered: {session_id}")
        return session_id
    
    async def unregister_connection(self, websocket: WebSocketServerProtocol):
        """Unregister a WebSocket connection"""
        self.active_connections.discard(websocket)
        # Remove session
        session_to_remove = None
        for session_id, session in self.audio_sessions.items():
            if session['websocket'] == websocket:
                session_to_remove = session_id
                break
        
        if session_to_remove:
            del self.audio_sessions[session_to_remove]
            logger.info(f"Connection unregistered: {session_to_remove}")
    
    async def handle_audio_input(self, session_id: str, audio_data: bytes):
        """Handle incoming audio data from frontend"""
        try:
            # Send audio to STT API container
            response = await self.stt_client.post(
                "http://stt-api:8003/transcribe",
                files={"audio": ("audio.wav", audio_data, "audio/wav")},
                timeout=30.0
            )
            
            if response.status_code == 200:
                transcription = response.json()
                logger.info(f"Transcription received: {transcription}")
                
                # Send transcription to brain API
                brain_response = await self.stt_client.post(
                    "http://brain-api:8000/process",
                    json={
                        "session_id": session_id,
                        "text": transcription.get("text", ""),
                        "confidence": transcription.get("confidence", 0.0)
                    }
                )
                
                if brain_response.status_code == 200:
                    brain_data = brain_response.json()
                    # Send response back to frontend
                    await self.send_to_frontend(session_id, {
                        "type": "transcription_result",
                        "data": brain_data
                    })
                    
                    # If there's a response to synthesize
                    if brain_data.get("response"):
                        await self.synthesize_response(session_id, brain_data["response"])
                
            else:
                logger.error(f"STT API error: {response.status_code}")
                await self.send_error(session_id, "STT processing failed")
                
        except Exception as e:
            logger.error(f"Audio processing error: {e}")
            await self.send_error(session_id, str(e))
    
    async def synthesize_response(self, session_id: str, text: str):
        """Synthesize text to speech using TTS API"""
        try:
            response = await self.tts_client.post(
                "http://tts-api:8002/synthesize",
                json={"text": text, "session_id": session_id},
                timeout=30.0
            )
            
            if response.status_code == 200:
                audio_data = response.content
                # Convert to base64 for WebSocket transmission
                audio_b64 = base64.b64encode(audio_data).decode('utf-8')
                
                await self.send_to_frontend(session_id, {
                    "type": "audio_response",
                    "data": {
                        "audio": audio_b64,
                        "text": text
                    }
                })
                
            else:
                logger.error(f"TTS API error: {response.status_code}")
                await self.send_error(session_id, "TTS synthesis failed")
                
        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            await self.send_error(session_id, str(e))
    
    async def send_to_frontend(self, session_id: str, message: dict):
        """Send message to frontend via WebSocket"""
        if session_id in self.audio_sessions:
            websocket = self.audio_sessions[session_id]['websocket']
            try:
                await websocket.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                logger.info(f"Connection closed for session {session_id}")
                await self.unregister_connection(websocket)
    
    async def send_error(self, session_id: str, error_msg: str):
        """Send error message to frontend"""
        await self.send_to_frontend(session_id, {
            "type": "error",
            "message": error_msg
        })
    
    async def handle_websocket(self, websocket: WebSocketServerProtocol, path: str):
        """Handle WebSocket connections"""
        session_id = await self.register_connection(websocket)
        
        try:
            # Send welcome message
            await websocket.send(json.dumps({
                "type": "connection_established",
                "session_id": session_id
            }))
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get("type")
                    
                    if msg_type == "audio_chunk":
                        # Handle audio streaming
                        audio_b64 = data.get("audio")
                        if audio_b64:
                            audio_data = base64.b64decode(audio_b64)
                            await self.handle_audio_input(session_id, audio_data)
                    
                    elif msg_type == "text_input":
                        # Handle direct text input
                        text = data.get("text")
                        if text:
                            brain_response = await self.stt_client.post(
                                "http://brain-api:8000/process",
                                json={
                                    "session_id": session_id,
                                    "text": text,
                                    "confidence": 1.0
                                }
                            )
                            
                            if brain_response.status_code == 200:
                                brain_data = brain_response.json()
                                await self.send_to_frontend(session_id, {
                                    "type": "text_response",
                                    "data": brain_data
                                })
                                
                                if brain_data.get("response"):
                                    await self.synthesize_response(session_id, brain_data["response"])
                    
                    elif msg_type == "ping":
                        await websocket.send(json.dumps({"type": "pong"}))
                    
                    else:
                        logger.warning(f"Unknown message type: {msg_type}")
                        
                except json.JSONDecodeError:
                    logger.error("Invalid JSON received")
                    await self.send_error(session_id, "Invalid JSON format")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket connection closed for session {session_id}")
        finally:
            await self.unregister_connection(websocket)

# Global audio bridge instance
audio_bridge = AudioBridge()

async def websocket_handler(websocket: WebSocketServerProtocol, path: str):
    """WebSocket endpoint handler"""
    await audio_bridge.handle_websocket(websocket, path)

async def start_audio_bridge_server():
    """Start the audio bridge WebSocket server"""
    server = await websockets.serve(
        websocket_handler,
        "0.0.0.0",
        8001,
        ping_interval=20,
        ping_timeout=10
    )
    logger.info("Audio Bridge WebSocket server started on ws://0.0.0.0:8001")
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(start_audio_bridge_server())
    except KeyboardInterrupt:
        logger.info("Audio Bridge server shutting down...")