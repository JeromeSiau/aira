"""
Main entry point for the application
Coordinates all agents and manages the main loop using LangGraph
"""

import asyncio
from queue import Queue
from typing import Dict, Any, List
import config

# LangGraph imports
from langgraph.graph import StateGraph
from pydantic import BaseModel, Field

# Import modules
from modules.emotion_manager import EmotionManager
from modules.llm_interface import LLMInterface
from modules.context_manager import ContextManager

# Import agents
from agents.animation_agent import AnimationAgent
from agents.speech_agent import SpeechAgent
from agents.conversation_agent import ConversationAgent

# Define state model for LangGraph
class AppState(BaseModel):
    """State model for the application"""
    user_input: str = ""
    response: Dict[str, Any] = Field(default_factory=dict)
    quit_requested: bool = False

# Define node functions
def process_user_input(state: AppState) -> AppState:
    """
    Process user input and update state
    
    Args:
        state: Current application state
        
    Returns:
        AppState: Updated state
    """
    # Check for exit command
    if state.user_input.lower() in ['exit', 'quit', 'bye']:
        print("Goodbye!")
        return AppState(
            user_input=state.user_input,
            response={},
            quit_requested=True
        )
    
    # Return state with empty response
    return AppState(
        user_input=state.user_input,
        response={},
        quit_requested=False
    )

def handle_conversation(state: AppState, conversation_agent: ConversationAgent) -> AppState:
    """
    Handle conversation with LLM
    
    Args:
        state: Current application state
        conversation_agent: Conversation agent instance
        
    Returns:
        AppState: Updated state with response
    """
    # Skip if exit was requested
    if state.quit_requested:
        return state
    
    # Process the input and generate response
    response = conversation_agent.process(state.user_input)
    
    # Create a new state with the response
    return AppState(
        user_input=state.user_input,
        response=response,
        quit_requested=state.quit_requested
    )

def display_output(state: AppState) -> AppState:
    """
    Display the output to the user
    
    Args:
        state: Current application state
        
    Returns:
        AppState: Same state, unmodified
    """
    # Skip if exit was requested
    if state.quit_requested:
        return state
    
    # Display response
    if state.response and "text" in state.response:
        print(f"AI: {state.response['text']}")
        print(f"Emotion: {state.response['emotion']}")
    
    return state

async def main():
    """Main function executed at startup"""
    print("Starting AI Companion...")
    
    # Create queues for inter-agent communication
    emotion_queue = Queue()
    speech_queue = Queue()
    user_input_queue = Queue()
    
    # Initialize and start agents
    animation_agent = AnimationAgent(input_queue=emotion_queue)
    animation_agent.start()
    
    speech_agent = SpeechAgent(input_queue=speech_queue)
    speech_agent.start()
    
    conversation_agent = ConversationAgent(
        input_queue=user_input_queue,
        emotion_queue=emotion_queue,
        speech_queue=speech_queue
    )
    conversation_agent.start()
    
    # Build LangGraph workflow
    workflow = StateGraph(AppState)
    
    # Add nodes
    workflow.add_node("process_input", process_user_input)
    
    # For the conversation node, we need to pass the agent
    # Using a closure to pass the agent to the function
    workflow.add_node("conversation", 
                     lambda state: handle_conversation(state, conversation_agent))
    
    workflow.add_node("display_output", display_output)
    
    # Add edges
    workflow.add_edge("process_input", "conversation")
    workflow.add_edge("conversation", "display_output")
    
    # Set entry and exit points
    workflow.set_entry_point("process_input")
    workflow.set_finish_point("display_output")
    
    # Compile the workflow
    graph = workflow.compile()
    
    # Main loop
    print("AI Companion ready! Type 'exit' to quit.")
    
    try:
        while True:
            # Get user input
            user_input = input("You: ")
            
            # Initialize state
            state = AppState(user_input=user_input)
            
            # Run workflow
            final_state = graph.invoke(state)
            
            # LangGraph can return different state types depending on version
            # Try both approaches to check quit flag
            quit_requested = False
            if hasattr(final_state, "quit_requested"):
                quit_requested = final_state.quit_requested
            elif hasattr(final_state, "get") and callable(final_state.get):
                quit_requested = final_state.get("quit_requested", False)
            elif isinstance(final_state, dict):
                quit_requested = final_state.get("quit_requested", False)
                
            if quit_requested:
                break
            
            # Pause to let other agents process
            await asyncio.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nInterrupted by user. Shutting down...")
    finally:
        # Properly stop all agents
        animation_agent.stop()
        speech_agent.stop()
        conversation_agent.stop()
        print("All agents stopped. Goodbye!")

# Program entry point
if __name__ == "__main__":
    # Start asyncio loop
    asyncio.run(main())