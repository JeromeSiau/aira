"""
Main entry point for the application
Coordinates all agents and manages the main loop
"""

import asyncio
from queue import Queue
import config

# Import modules
from modules.emotion_manager import EmotionManager
from modules.llm_interface import LLMInterface
from modules.context_manager import ContextManager

# Import agents
from agents.animation_agent import AnimationAgent
from agents.speech_agent import SpeechAgent  # To be implemented
# from agents.conversation_agent import ConversationAgent  # If you want to make it a separate agent

async def main():
    """Main function executed at startup"""
    print("Starting AI Companion...")
    
    # Create queues for inter-agent communication
    emotion_queue = Queue()
    speech_queue = Queue()
    
    # Initialize managers
    emotion_manager = EmotionManager()
    llm = LLMInterface()
    context = ContextManager()
    
    # Initialize and start agents
    animation_agent = AnimationAgent(input_queue=emotion_queue)
    animation_agent.start()
    
    speech_agent = SpeechAgent(input_queue=speech_queue)
    speech_agent.start()
    
    # Add system message to define personality
    context.add_system_message(config.SYSTEM_PROMPT)
    
    # Main loop
    print("AI Companion ready! Type 'exit' to quit.")
    
    try:
        while True:
            # Get user input
            user_input = input("You: ")
            
            # Check if user wants to quit
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break
                
            # Add user message to context
            context.add_user_message(user_input)
            
            # Check if summary is needed
            if context.should_summarize():
                print("DEBUG - Creating summary to optimize context...")
                context.create_summary()
            
            # Get messages in Ollama format
            ollama_messages = context.get_ollama_messages()
            
            # Generate response
            response = llm.generate_response(ollama_messages)
            response_content = llm.extract_content(response)
            
            # Extract text and emotion
            clean_text, emotion = emotion_manager.extract_emotion(response_content)
            
            # Display response
            print(f"AI: {clean_text}")
            print(f"Emotion: {emotion}")
            
            # Add response to context
            context.add_ai_message(response_content, {"emotion": emotion})
            
            # Send emotion and text to agents
            emotion_queue.put(emotion)
            speech_queue.put(clean_text)
            
            # Display context statistics
            print(f"DEBUG - Context: {context.token_count} tokens (~{context.token_count/config.MAX_CONTEXT_TOKENS*100:.1f}%)")
            if context.summary:
                print(f"DEBUG - Using summary: {context.summary[:50]}...")
            
            # Pause to let other agents process
            await asyncio.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nInterrupted by user. Shutting down...")
    finally:
        # Properly stop all agents
        animation_agent.stop()
        speech_agent.stop()
        print("All agents stopped. Goodbye!")

# Program entry point
if __name__ == "__main__":
    # Start asyncio loop
    asyncio.run(main())