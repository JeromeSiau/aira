"""
Utilities for token count estimation
"""

from typing import List, Dict, Any, Union

def count_tokens(text: str) -> int:
    """
    Simple estimation of token count in text
    
    Args:
        text: Text to analyze
        
    Returns:
        int: Estimated token count
    """
    # Rough estimation: ~4 characters = 1 token on average for BPE-based models
    return len(text) // 4 + 1

def estimate_message_tokens(messages: List[Dict[str, str]]) -> int:
    """
    Estimates total token count in a list of messages
    
    Args:
        messages: Message list in format [{role, content}, ...]
        
    Returns:
        int: Estimated total token count
    """
    total = 0
    
    for message in messages:
        # Count content
        if 'content' in message:
            total += count_tokens(message['content'])
        
        # Add fixed cost for metadata
        total += 4  # ~4 tokens for role, format, etc.
    
    return total

def format_token_count(count: int) -> str:
    """
    Format token count for display
    
    Args:
        count: Token count
        
    Returns:
        str: Formatted representation (e.g., "1.2K")
    """
    if count < 1000:
        return str(count)
    return f"{count/1000:.1f}K"