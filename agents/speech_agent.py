"""
Agent responsible for speech synthesis
"""

from queue import Queue, Empty  # Import Empty exception directly
from typing import Optional
import time
from agents.base_agent import BaseAgent
from modules.emotion_manager import EmotionManager
from openai import OpenAI
import pyaudio
import threading

class SpeechAgent(BaseAgent):
    """Agent managing speech synthesis"""
    
    def __init__(self, input_queue: Queue = None):
        """
        Initialize speech synthesis agent
        
        Args:
            input_queue: Queue for texts to synthesize
        """
        super().__init__("Speech", input_queue)
        self.emotion_manager = EmotionManager()
        self.is_speaking = False
        self.current_text = ""
        
        # Initialize Kokoro TTS client
        self.client = OpenAI(
            base_url="http://localhost:8880/v1", 
            api_key="not-needed"
        )
        
        # Initialize PyAudio player
        self.pyaudio_instance = pyaudio.PyAudio()
        self.player = None
        self.stop_requested = False
        self.tts_thread = None
    
    def process(self, text: str) -> None:
        """
        Process new text to synthesize
        
        Args:
            text: Text to synthesize
            
        Returns:
            None
        """
        # Clean text of emotion tags
        clean_text = self.emotion_manager.strip_emotions(text)
        
        if not clean_text.strip():
            print("WARNING - Empty text received for speech synthesis")
            return None
        
        # Interrupt any ongoing speech
        self.interrupt()
        
        # Mark as speaking
        self.is_speaking = True
        self.current_text = clean_text
        self.stop_requested = False
        
        print(f"DEBUG - Speech synthesis: '{clean_text}'")
        
        # Start synthesis in a separate thread
        self.tts_thread = threading.Thread(
            target=self._synthesize_and_play,
            args=(clean_text,)
        )
        self.tts_thread.start()
        
        return None
    
    def _synthesize_and_play(self, text: str) -> None:
        """
        Synthesize text and stream to speakers
        
        Args:
            text: Text to synthesize
        """
        try:
            # Initialize player for this session
            self.player = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=24000,
                output=True
            )
            
            # Stream synthesis to speakers
            with self.client.audio.speech.with_streaming_response.create(
                model="kokoro",
                voice="af_bella",  # You may want to make this configurable
                response_format="pcm",
                input=text
            ) as response:
                for chunk in response.iter_bytes(chunk_size=1024):
                    if self.stop_requested:
                        break
                    self.player.write(chunk)
                    
        except Exception as e:
            print(f"ERROR - Speech synthesis failed: {e}")
        finally:
            # Clean up resources
            if self.player:
                self.player.stop_stream()
                self.player.close()
                self.player = None
            
            # Mark as finished speaking
            self.is_speaking = False
    
    def is_busy(self) -> bool:
        """
        Indicates if agent is busy speaking
        
        Returns:
            bool: True if agent is speaking
        """
        return self.is_speaking
    
    def interrupt(self) -> None:
        """
        Interrupts ongoing speech synthesis
        """
        if self.is_speaking:
            print("DEBUG - Speech interrupted")
            self.stop_requested = True
            
            # Wait for thread to finish
            if self.tts_thread and self.tts_thread.is_alive():
                self.tts_thread.join(timeout=1.0)
                
            # Clean up if thread didn't exit properly
            if self.player:
                self.player.stop_stream()
                self.player.close()
                self.player = None
                
            self.is_speaking = False