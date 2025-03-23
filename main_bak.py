import asyncio
import json
from queue import Queue
import threading
from typing import Dict, Any, List

# CONVERSATION AGENT (LANGGRAPH)
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
import re
import ollama

class ConversationState(BaseModel):
    messages: List[AIMessage | HumanMessage] = Field(default_factory=list)
    emotion: str = "neutral"  # Current emotional state

# Queues for inter-agent communication
emotion_queue = Queue()  # To send emotions to the animation agent
speech_queue = Queue()   # To send text to the TTS agent

# Personality definition
personality = """You are a demon girl who dreams of conquering the world, but deep down you're just a cute child.

CRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE EXACTLY:
1. You will ONLY respond to the user's message provided in 'Last message:'
2. You will NEVER generate additional messages or continue the conversation
3. You will NEVER pretend to be the user or generate user messages
4. Keep responses short (max 2-3 sentences)
5. ALWAYS end your response with exactly ONE emotion in brackets
6. Available emotions: [excited], [evil], [embarrassed], [annoyed], [curious], [triumphant], [sad], [neutral]

Example format:
Last message: Hello, what's your name?
Response: I am Lilith, future ruler of this world! *giggles* [excited]
"""

# Define the functions with clearer input/output expectations
def add_user_message(state, values):
    """Process user input and add it to the message history"""
    # Extract user_input from values
    user_input = values["user_input"]
    
    # Create a new state with the user message added
    new_messages = add_messages(state["messages"], [HumanMessage(content=user_input)])
    
    return {
        "messages": new_messages,
        "emotion": state["emotion"]
    }

def generate_response(state):
    """Generate AI response based on conversation history"""
    # Get the last user message
    messages = state["messages"]
    last_user_message = messages[-1].content if messages else ""
    
    prompt = f"""SYSTEM: You are a demon girl who dreams of conquering the world, but deep down you're just a cute child.

YOU MUST FOLLOW THESE RULES EXACTLY:
1. ONLY answer the most recent user message: "{last_user_message}"
2. NEVER generate text as if you were the user
3. NEVER include text like "User:" or "A:" in your response
4. DO NOT roleplay both sides of a conversation
5. Keep responses under 100 characters
6. End with exactly ONE emotion tag: [excited], [evil], [embarrassed], [annoyed], [curious], [triumphant], [sad], [neutral]

USER: {last_user_message}

Your response (remember to end with ONE emotion tag):"""
    
    ollama_response = ollama.chat(model="gemma3:27b-it-q8_0", messages=[{"role": "user", "content": prompt}])
    print(f"DEBUG - Raw response: {ollama_response}")
    
    # Extract the text content from the response object
    full_response = ollama_response.message.content if hasattr(ollama_response, 'message') else str(ollama_response)
    
    # Nettoyage plus agressif - supprimer tout ce qui ressemble à un dialogue
    clean_response = re.sub(r"(?i)user:.*", "", full_response)
    clean_response = re.sub(r"(?i)a:.*?(\[|$)", "", clean_response)
    clean_response = re.sub(r"(?i)last message:.*", "", clean_response)
    clean_response = re.sub(r"(?i)response:.*?(\[|$)", "", clean_response)
    
    # Supprimer tout texte après une nouvelle ligne (souvent utilisé pour commencer un nouveau tour)
    if "\n" in clean_response:
        clean_response = clean_response.split("\n")[0]
    
    # Extraire l'émotion
    emotion_pattern = r"\[(excited|evil|embarrassed|annoyed|curious|triumphant|sad|neutral)\]"
    emotion_matches = list(re.finditer(emotion_pattern, clean_response.lower()))
    
    if not emotion_matches:
        detected_emotion = "neutral"
        # S'assurer qu'il y a du texte avant d'ajouter l'émotion
        if clean_response.strip():
            clean_response = f"{clean_response.strip()} [neutral]"
        else:
            clean_response = f"I acknowledge your message. [neutral]"
    else:
        detected_emotion = emotion_matches[-1].group(1)
        clean_response = re.sub(emotion_pattern, "", clean_response).strip()
        
        # Si après avoir supprimé l'émotion, la réponse est vide, ajouter un texte par défaut
        if not clean_response:
            default_responses = {
                "excited": "This is so exciting!",
                "evil": "I have sinister plans for this world...",
                "embarrassed": "Oh, um... *fidgets nervously*",
                "annoyed": "Hmph! How annoying.",
                "curious": "Hmm, that's interesting...",
                "triumphant": "Ha! Just as I planned!",
                "sad": "That makes me feel sad...",
                "neutral": "I see. Interesting."
            }
            clean_response = default_responses.get(detected_emotion, "I see.")
        
        clean_response = f"{clean_response} [{detected_emotion}]"
    
    # Garantir que la réponse n'est pas trop longue
    if len(clean_response) > 100:
        clean_response = clean_response[:97] + "..."
    
    print(f"DEBUG - Clean response: {clean_response}")
    
    # Envoyer l'émotion et le texte aux autres agents
    emotion_queue.put(detected_emotion)
    speech_queue.put(clean_response)
    
    # Create AI message with emotion in metadata
    ai_message = AIMessage(content=clean_response, metadata={"emotion": detected_emotion})
    
    # Add AI message to conversation history
    new_messages = add_messages(messages, [ai_message])
    
    return {
        "messages": new_messages,
        "emotion": detected_emotion
    }

# Build a simpler workflow
workflow = StateGraph(ConversationState)

# For the user input node, we need to handle both the state and the user input
workflow.add_node("add_user_message", add_user_message)
workflow.add_node("generate_response", generate_response)

# Configure the workflow
workflow.add_edge("add_user_message", "generate_response")
workflow.set_entry_point("add_user_message")
workflow.set_finish_point("generate_response")

# Compile the workflow
graph = workflow.compile()

# ANIMATION AGENT (SEPARATE THREAD)
def animation_agent():
    current_emotion = "neutral"
    animations = {
        "excited": "bouncing_excited.anim",
        "evil": "evil_scheme.anim",
        "embarrassed": "blushing.anim",
        "annoyed": "pouting.anim",
        "curious": "head_tilt.anim",
        "triumphant": "victory_pose.anim",
        "sad": "sad_eyes.anim",
        "neutral": "idle.anim"
    }
    
    print("Animation Agent started")
    
    while True:
        try:
            # Non-blocking with timeout to regularly check
            new_emotion = emotion_queue.get(timeout=0.1)
            
            if new_emotion != current_emotion:
                print(f"Emotion change: {current_emotion} -> {new_emotion}")
                # Here, you would call your animation engine
                # animate(animations[new_emotion])
                current_emotion = new_emotion
                
                # Simulate animation
                print(f"Animation: {animations[new_emotion]}")
        except:
            # No new emotion, continue current animation
            # idle_animation(current_emotion)
            pass

# TTS AGENT (SEPARATE THREAD)
def tts_agent():
    print("TTS Agent started")
    
    while True:
        try:
            # Wait for text to synthesize
            text = speech_queue.get(timeout=0.1)
            
            # Here, you would call your TTS engine
            print(f"Speech synthesis: '{text}'")
            
            # Simulate synthesis and pronunciation time
            # In production, you would synchronize with facial animations
            # tts_engine.synthesize(text)
        except:
            # No new text to synthesize
            pass

# AGENT COORDINATION
async def main():
    # Start animation and TTS agents in separate threads
    animation_thread = threading.Thread(target=animation_agent, daemon=True)
    tts_thread = threading.Thread(target=tts_agent, daemon=True)
    
    animation_thread.start()
    tts_thread.start()
    
    # Créons notre propre système simple sans LangGraph pour éviter les problèmes
    state = {
        "messages": [],
        "emotion": "neutral"
    }
    
    # Main conversation loop
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Goodbye!")
                break
            
            # Traitement manuel des étapes au lieu d'utiliser LangGraph
            # 1. Ajouter le message utilisateur
            values = {"user_input": user_input}
            state = add_user_message(state, values)
            
            # 2. Générer la réponse
            state = generate_response(state)
            
            # Afficher la réponse
            messages = state["messages"]
            if messages:
                ai_messages = [msg for msg in messages if isinstance(msg, AIMessage)]
                if ai_messages:
                    latest_ai_message = ai_messages[-1]
                    # Afficher sans l'émotion à la fin
                    text_response = latest_ai_message.content
                    # Enlever l'émotion du texte si elle est toujours présente
                    emotion_pattern = r"\[(excited|evil|embarrassed|annoyed|curious|triumphant|sad|neutral)\]"
                    clean_text = re.sub(emotion_pattern, "", text_response).strip()
                    
                    # Vérifier que le texte n'est pas vide
                    if not clean_text:
                        emotion = latest_ai_message.metadata.get("emotion", "neutral")
                        default_responses = {
                            "excited": "This is so exciting!",
                            "evil": "I have sinister plans for this world...",
                            "embarrassed": "Oh, um... *fidgets nervously*",
                            "annoyed": "Hmph! How annoying.",
                            "curious": "Hmm, that's interesting...",
                            "triumphant": "Ha! Just as I planned!",
                            "sad": "That makes me feel sad...",
                            "neutral": "I see. Interesting."
                        }
                        clean_text = default_responses.get(emotion, "I see.")
                    
                    print(f"AI: {clean_text}")
                    if "emotion" in latest_ai_message.metadata:
                        print(f"Emotion: {latest_ai_message.metadata['emotion']}")
            
            # Wait a bit to let TTS and animation finish
            await asyncio.sleep(0.1)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

if __name__ == "__main__":
    asyncio.run(main())