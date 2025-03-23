"""
Agent responsible for speech synthesis
"""

from queue import Queue, Empty  # Import Empty exception directly
from typing import Optional
import time
from agents.base_agent import BaseAgent
from modules.emotion_manager import EmotionManager

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
        
        # Here, you would initialize your TTS engine
        # self.tts_engine = initialize_tts_engine()
    
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
        
        # Mark as speaking
        self.is_speaking = True
        self.current_text = clean_text
        
        print(f"DEBUG - Speech synthesis: '{clean_text}'")
        
        # Here, you would call your actual TTS engine
        # audio_data = self.tts_engine.synthesize(clean_text)
        # play_audio(audio_data)
        
        # Simulate synthesis and pronunciation time (about 0.1s per word)
        word_count = len(clean_text.split())
        estimated_duration = max(0.5, word_count * 0.1)  # At least 0.5s
        
        print(f"DEBUG - Speech duration: ~{estimated_duration:.1f}s")
        
        # Simulate speech duration
        time.sleep(estimated_duration)
        
        # Mark as finished speaking
        self.is_speaking = False
        
        return None
    
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
            # Here, you would stop the ongoing synthesis
            # self.tts_engine.stop()
            self.is_speaking = False