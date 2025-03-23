"""
Global configuration for all application modules
"""

# LLM Configuration
LLM_MODEL = "gemma3:27b-it-q8_0"
MAX_CONTEXT_TOKENS = 10000
SUMMARY_THRESHOLD = 0.7  # Summarize at 70% of max context
DEFAULT_TEMPERATURE = 0.7
SUMMARY_TEMPERATURE = 0.3

# Response Configuration
MAX_RESPONSE_LENGTH = 250
DEFAULT_EMOTION = "neutral"

# Prompts
SYSTEM_PROMPT = f"""You are a demon girl who dreams of conquering the world, but deep down you're just a cute child.

YOU MUST FOLLOW THESE RULES EXACTLY:
1. Keep responses under {MAX_RESPONSE_LENGTH} characters
2. End with exactly ONE emotion tag: [excited], [evil], [embarrassed], [annoyed], [curious], [triumphant], [sad], [neutral]
3. Don't repeat what the user said
4. Remember all previous information in the conversation"""

SUMMARY_PROMPT = f"""Concisely summarize our conversation so far. 
Include only important information like my identity and our relationship, 
as well as the main topics discussed. Maximum {MAX_RESPONSE_LENGTH} words."""

# Available emotions
VALID_EMOTIONS = [
    "excited", 
    "evil", 
    "embarrassed", 
    "annoyed", 
    "curious", 
    "triumphant", 
    "sad", 
    "neutral"
]

# Default responses by emotion
DEFAULT_RESPONSES = {
    "excited": "This is so exciting!",
    "evil": "I have sinister plans for this world...",
    "embarrassed": "Oh, um... *fidgets nervously*",
    "annoyed": "Hmph! How annoying.",
    "curious": "Hmm, that's interesting...",
    "triumphant": "Ha! Just as I planned!",
    "sad": "That makes me feel sad...",
    "neutral": "I see. Interesting."
}

# Animations
ANIMATIONS = {
    "excited": "bouncing_excited.anim",
    "evil": "evil_scheme.anim",
    "embarrassed": "blushing.anim",
    "annoyed": "pouting.anim",
    "curious": "head_tilt.anim",
    "triumphant": "victory_pose.anim",
    "sad": "sad_eyes.anim",
    "neutral": "idle.anim"
}