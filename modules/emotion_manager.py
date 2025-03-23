"""
Emotion management module
Centralizes emotion detection, cleaning, and management
"""

import re
from typing import Tuple
import config

class EmotionManager:
    """Centralized emotion manager"""
    
    def __init__(self):
        """Initialize emotion manager"""
        self.current_emotion = config.DEFAULT_EMOTION
        self.emotion_pattern = r"\[(excited|evil|embarrassed|annoyed|curious|triumphant|sad|neutral)\]"
    
    def extract_emotion(self, text: str) -> Tuple[str, str]:
        """
        Extract emotion from text and return cleaned text and emotion
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple[str, str]: (cleaned_text, emotion)
        """
        # Find all emotion occurrences
        emotion_matches = list(re.finditer(self.emotion_pattern, text.lower()))
        
        if not emotion_matches:
            # No emotion found, use default
            detected_emotion = config.DEFAULT_EMOTION
            clean_text = text.strip()
        else:
            # Take the last emotion (in case of multiple)
            detected_emotion = emotion_matches[-1].group(1)
            # Clean all emotion tags
            clean_text = re.sub(self.emotion_pattern, "", text).strip()
        
        # Check if text is empty after cleaning
        if not clean_text:
            clean_text = config.DEFAULT_RESPONSES.get(detected_emotion, "I see.")
        
        # Update current emotion
        self.current_emotion = detected_emotion
        
        return clean_text, detected_emotion
    
    def strip_emotions(self, text: str) -> str:
        """
        Remove all emotion tags from text
        
        Args:
            text: Text to clean
            
        Returns:
            str: Text without emotion tags
        """
        return re.sub(self.emotion_pattern, "", text).strip()
    
    def add_emotion_tag(self, text: str, emotion: str = None) -> str:
        """
        Add emotion tag to text
        
        Args:
            text: Text to tag
            emotion: Emotion to add (uses current emotion if None)
            
        Returns:
            str: Text with emotion tag
        """
        if emotion is None:
            emotion = self.current_emotion
            
        # Ensure emotion is valid
        if emotion not in config.VALID_EMOTIONS:
            emotion = config.DEFAULT_EMOTION
            
        # First clean text of any existing tags
        clean_text = self.strip_emotions(text)
        
        # Add tag at the end
        return f"{clean_text} [{emotion}]"
    
    def get_default_response(self, emotion: str = None) -> str:
        """
        Return default response for a given emotion
        
        Args:
            emotion: Emotion (uses current emotion if None)
            
        Returns:
            str: Default response for this emotion
        """
        if emotion is None:
            emotion = self.current_emotion
            
        return config.DEFAULT_RESPONSES.get(emotion, "I see.")
    
    def get_animation_file(self, emotion: str = None) -> str:
        """
        Return animation file for a given emotion
        
        Args:
            emotion: Emotion (uses current emotion if None)
            
        Returns:
            str: Animation filename
        """
        if emotion is None:
            emotion = self.current_emotion
            
        return config.ANIMATIONS.get(emotion, config.ANIMATIONS[config.DEFAULT_EMOTION])