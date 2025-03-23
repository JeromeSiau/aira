"""
Context manager for conversations
Handles history, summaries, and context optimization
"""

from typing import List, Dict, Any, Tuple
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import config
from utils.token_counter import count_tokens
from modules.llm_interface import LLMInterface
from modules.emotion_manager import EmotionManager

class ContextManager:
    """Context manager for conversations"""
    
    def __init__(self):
        """Initialize context manager"""
        self.messages = []  # LangChain messages
        self.token_count = 0
        self.summary = ""
        self.llm = LLMInterface()
        self.emotion_manager = EmotionManager()
    
    def add_system_message(self, content: str) -> None:
        """
        Add a system message
        
        Args:
            content: System message content
        """
        self.messages.append(SystemMessage(content=content))
        self.token_count += count_tokens(content)
    
    def add_user_message(self, content: str) -> None:
        """
        Add a user message
        
        Args:
            content: User message content
        """
        self.messages.append(HumanMessage(content=content))
        self.token_count += count_tokens(content)
    
    def add_ai_message(self, content: str, metadata: Dict[str, Any] = None) -> None:
        """
        Add an AI message
        
        Args:
            content: AI message content
            metadata: Message metadata (emotion, etc.)
        """
        if metadata is None:
            metadata = {}
        
        # If content contains an emotion, extract it
        clean_content, emotion = self.emotion_manager.extract_emotion(content)
        
        # Add emotion to metadata
        metadata["emotion"] = emotion
        
        # Add message to history
        self.messages.append(AIMessage(content=content, metadata=metadata))
        self.token_count += count_tokens(content)
    
    def should_summarize(self) -> bool:
        """
        Determine if context should be summarized
        
        Returns:
            bool: True if context should be summarized
        """
        return self.token_count > config.MAX_CONTEXT_TOKENS * config.SUMMARY_THRESHOLD
    
    def create_summary(self) -> None:
        """
        Create a summary of the current conversation
        """
        if not self.messages:
            return
            
        # Convert LangChain messages to Ollama format
        ollama_messages = []
        
        # Add system message to define personality
        ollama_messages.append({
            "role": "system",
            "content": config.SYSTEM_PROMPT
        })
        
        # Add all messages
        for msg in self.messages:
            if isinstance(msg, HumanMessage):
                ollama_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                # Clean emotions
                clean_content = self.emotion_manager.strip_emotions(msg.content)
                ollama_messages.append({"role": "assistant", "content": clean_content})
        
        # Generate summary
        self.summary = self.llm.generate_summary(ollama_messages)
        print(f"DEBUG - New summary created: {self.summary[:50]}...")
        
        # Keep only the last 3 exchanges
        self.prune_conversation(3)
        
        # Recalculate token count
        self.recalculate_tokens()
    
    def prune_conversation(self, keep_exchanges: int) -> None:
        """
        Keep only a certain number of recent exchanges
        
        Args:
            keep_exchanges: Number of exchanges to keep
        """
        if len(self.messages) <= keep_exchanges * 2:
            return
            
        # Calculate index from which to keep messages
        start_idx = max(0, len(self.messages) - (keep_exchanges * 2))
        self.messages = self.messages[start_idx:]
    
    def recalculate_tokens(self) -> None:
        """
        Recalculate token count in current conversation
        """
        self.token_count = 0
        
        # Count summary tokens
        if self.summary:
            self.token_count += count_tokens(self.summary)
        
        # Count tokens for all messages
        for msg in self.messages:
            self.token_count += count_tokens(msg.content)
    
    def get_ollama_messages(self) -> List[Dict[str, str]]:
        """
        Convert messages to Ollama format
        
        Returns:
            List[Dict[str, str]]: Messages in Ollama format
        """
        ollama_messages = []
        
        # Add system message to define personality
        ollama_messages.append({
            "role": "system",
            "content": config.SYSTEM_PROMPT
        })
        
        # If we have a summary, add it at the beginning of the context
        if self.summary:
            ollama_messages.append({
                "role": "user",
                "content": f"Here's a summary of our previous conversation: {self.summary}"
            })
            ollama_messages.append({
                "role": "assistant",
                "content": "I remember our conversation. Let's continue."
            })
        
        # Add all messages
        for msg in self.messages:
            if isinstance(msg, HumanMessage):
                ollama_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                # Clean emotions
                clean_content = self.emotion_manager.strip_emotions(msg.content)
                ollama_messages.append({"role": "assistant", "content": clean_content})
        
        return ollama_messages
    
    def get_latest_ai_message(self) -> Tuple[str, str]:
        """
        Return the latest AI message and its emotion
        
        Returns:
            Tuple[str, str]: (content, emotion)
        """
        for msg in reversed(self.messages):
            if isinstance(msg, AIMessage):
                content = msg.content
                emotion = msg.metadata.get("emotion", config.DEFAULT_EMOTION)
                # Clean emotions from content
                clean_content = self.emotion_manager.strip_emotions(content)
                return clean_content, emotion
        
        return "", config.DEFAULT_EMOTION