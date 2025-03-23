"""
Interface with language models (LLM)
Abstracts calls to Ollama and other backends
"""

import time
import ollama
from typing import List, Dict, Any, Optional
import config
from utils.token_counter import estimate_message_tokens

class LLMInterface:
    """Interface for language model interactions"""
    
    def __init__(self, model_name: str = None):
        """
        Initialize LLM interface
        
        Args:
            model_name: Model name to use (default: config.LLM_MODEL)
        """
        self.model_name = model_name or config.LLM_MODEL
        self.last_response_time = 0
    
    def generate_response(self, 
                         messages: List[Dict[str, str]], 
                         temperature: float = None,
                         max_context: int = None) -> Dict[str, Any]:
        """
        Generate a response from a list of messages
        
        Args:
            messages: List of messages in format [{role, content}, ...]
            temperature: Temperature for generation (default: config.DEFAULT_TEMPERATURE)
            max_context: Maximum context size (default: config.MAX_CONTEXT_TOKENS)
            
        Returns:
            Dict: Complete model response
        """
        temperature = temperature or config.DEFAULT_TEMPERATURE
        max_context = max_context or config.MAX_CONTEXT_TOKENS
        
        # Estimate token count
        token_count = estimate_message_tokens(messages)
        print(f"DEBUG - Sending approx. {token_count} tokens to LLM")
        
        # Measure response time
        start_time = time.time()
        
        try:
            # Call Ollama with configured options
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": temperature,
                    "num_ctx": max_context
                }
            )
            
            # Measure and store response time
            self.last_response_time = time.time() - start_time
            print(f"DEBUG - Response time: {self.last_response_time:.2f} seconds")
            
            return response
            
        except Exception as e:
            print(f"ERROR - LLM call failed: {str(e)}")
            # Return error response
            return {
                "message": {
                    "role": "assistant",
                    "content": f"I'm having trouble thinking right now. [confused]"
                }
            }
    
    def extract_content(self, response: Dict[str, Any]) -> str:
        """
        Extract text content from a response
        
        Args:
            response: Model response
            
        Returns:
            str: Text content
        """
        if hasattr(response, 'message') and hasattr(response.message, 'content'):
            return response.message.content
        elif isinstance(response, dict) and 'message' in response:
            if isinstance(response['message'], dict) and 'content' in response['message']:
                return response['message']['content']
            elif hasattr(response['message'], 'content'):
                return response['message'].content
        
        # Fallback if structure is unknown
        return str(response)
    
    def generate_summary(self, conversation_messages: List[Dict[str, str]]) -> str:
        """
        Generate a summary of the conversation
        
        Args:
            conversation_messages: Conversation messages
            
        Returns:
            str: Generated summary
        """
        # Add summary request to messages
        summary_request = {
            "role": "user",
            "content": config.SUMMARY_PROMPT
        }
        
        # Call LLM with low temperature for factual summary
        summary_response = self.generate_response(
            messages=conversation_messages + [summary_request],
            temperature=config.SUMMARY_TEMPERATURE
        )
        
        # Extract summary content
        summary_text = self.extract_content(summary_response)
        
        return summary_text