"""
Agent responsible for character animations
"""

from queue import Queue, Empty  # Import Empty exception directly
from agents.base_agent import BaseAgent
from modules.emotion_manager import EmotionManager
import config

class AnimationAgent(BaseAgent):
    """Agent managing emotion-based animations"""
    
    def __init__(self, input_queue: Queue = None):
        """
        Initialize animation agent
        
        Args:
            input_queue: Queue for incoming emotions
        """
        super().__init__("Animation", input_queue)
        self.emotion_manager = EmotionManager()
        self.current_emotion = config.DEFAULT_EMOTION
    
    def process(self, emotion: str) -> None:
        """
        Process a new received emotion
        
        Args:
            emotion: Emotion to animate
            
        Returns:
            None
        """
        # Check that emotion is valid
        if emotion not in config.VALID_EMOTIONS:
            print(f"WARNING - Animation received invalid emotion: {emotion}")
            return None
            
        # If emotion has changed, update and animate
        if emotion != self.current_emotion:
            print(f"DEBUG - Emotion change: {self.current_emotion} -> {emotion}")
            self.current_emotion = emotion
            
            # Get animation file
            animation_file = self.emotion_manager.get_animation_file(emotion)
            
            # Here, you would start the actual animation
            # animate(animation_file)
            print(f"DEBUG - Playing animation: {animation_file}")
            
            return None
            
        # Same emotion, nothing to do
        return None
    
    def _run(self) -> None:
        """
        Main loop for animation agent
        Override to add continuous animation logic
        """
        while self.running:
            try:
                # Get new emotion with timeout
                emotion = self.input_queue.get(timeout=0.1)
                self.process(emotion)
                
            except Empty:
                # This is a normal queue timeout, just continue
                pass
            except Exception as e:
                # Log other exceptions
                print(f"ERROR - Animation agent error: {str(e)}")
            
            # Here, you could have continuous animation logic
            # based on current emotion, even without new emotion
            # For example, to make character breathe, blink, etc.
            # continuous_animation(self.current_emotion)