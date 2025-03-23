"""
Agent responsible for LLM interactions and conversation management
"""

from queue import Queue, Empty
from typing import Dict, Any
from agents.base_agent import BaseAgent
from modules.llm_interface import LLMInterface
from modules.context_manager import ContextManager
from modules.emotion_manager import EmotionManager
import config

class ConversationAgent(BaseAgent):
    """Agent managing conversation with the LLM"""
    
    def __init__(self, input_queue: Queue = None, emotion_queue: Queue = None, speech_queue: Queue = None):
        """
        Initialize conversation agent
        
        Args:
            input_queue: Queue for incoming user inputs
            emotion_queue: Queue to send emotions
            speech_queue: Queue to send speech text
        """
        super().__init__("Conversation", input_queue)
        self.llm = LLMInterface()
        self.context = ContextManager()
        self.emotion_manager = EmotionManager()
        self.emotion_queue = emotion_queue
        self.speech_queue = speech_queue
        
        # Add system message to define personality
        self.context.add_system_message(config.SYSTEM_PROMPT)
    
    def process(self, user_input: str) -> Dict[str, Any]:
        """
        Process a user input and generate a response
        
        Args:
            user_input: User's message
            
        Returns:
            Dict[str, Any]: Response information
        """
        # Add user message to context
        self.context.add_user_message(user_input)
        
        # Check if summary is needed
        if self.context.should_summarize():
            print("DEBUG - Creating summary to optimize context...")
            self.context.create_summary()
        
        # Get messages in Ollama format
        ollama_messages = self.context.get_ollama_messages()
        
        # Generate response
        response = self.llm.generate_response(ollama_messages)
        response_content = self.llm.extract_content(response)
        
        # Extract text and emotion
        clean_text, emotion = self.emotion_manager.extract_emotion(response_content)
        
        # Add response to context
        self.context.add_ai_message(response_content, {"emotion": emotion})
        
        # Send emotion and text to appropriate agents
        if self.emotion_queue:
            self.emotion_queue.put(emotion)
        
        if self.speech_queue:
            self.speech_queue.put(clean_text)
        
        # Display context statistics
        print(f"DEBUG - Context: {self.context.token_count} tokens (~{self.context.token_count/config.MAX_CONTEXT_TOKENS*100:.1f}%)")
        if self.context.summary:
            print(f"DEBUG - Using summary: {self.context.summary[:50]}...")
        
        return {
            "text": clean_text,
            "emotion": emotion,
            "token_count": self.context.token_count
        }