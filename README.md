# AIRA4 - Animated Intelligent Responsive Assistant

AIRA4 is an advanced AI companion system that combines large language models (LLMs) with emotion-based animations and voice synthesis to create an interactive, emotionally responsive character.

## Project Overview

This project creates a demonic girl character who dreams of conquering the world but is actually just a cute child at heart. The system maintains consistent memory, expresses emotions through animations, and communicates through voice synthesis.

### Key Features

- **Intelligent Conversations**: Powered by Gemma 3 27B running locally via Ollama
- **Emotion-Aware Responses**: Each response includes an emotion tag that drives animations
- **Animated Character**: Character animations change based on emotional state
- **Voice Synthesis**: Text-to-speech converts the AI's responses to voice
- **Long-Term Memory**: Context management with automatic summarization to handle long conversations

## Project Structure

```
aira4/
│
├── main.py                          # Main entry point
├── config.py                        # Centralized global configuration
│
├── modules/                         # Folder for all functional modules
│   ├── __init__.py
│   ├── emotion_manager.py           # Centralized emotion management
│   ├── speech_manager.py            # Speech and TTS management
│   ├── animation_manager.py         # Animation management
│   ├── context_manager.py           # Context and summary management
│   └── llm_interface.py             # Interface with Ollama/models
│
├── utils/                           # Shared utilities
│   ├── __init__.py
│   ├── token_counter.py             # Token estimation
│   └── text_processors.py           # Text cleaning and processing
│
└── agents/                          # Agent system
    ├── __init__.py
    ├── base_agent.py                # Base class for agents
    ├── conversation_agent.py        # Main conversation agent
    ├── animation_agent.py           # Animation agent
    └── speech_agent.py              # Speech synthesis agent
```

## System Architecture

AIRA4 uses a multi-agent architecture with separate components communicating through thread-safe queues:

1. **Main Loop**: Coordinates the overall conversation flow
2. **LLM Interface**: Handles interactions with the language model (Gemma 3 27B via Ollama)
3. **Context Manager**: Maintains conversation history and handles context optimization
4. **Emotion Manager**: Extracts, processes, and manages emotional states
5. **Animation Agent**: Plays animations based on emotional state
6. **Speech Agent**: Converts text to speech for audible responses

## Requirements

- Python 3.8+
- Ollama with Gemma 3 27B installed
- LangGraph
- Additional requirements listed in requirements.txt

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/aira4.git
cd aira4
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Ensure Ollama is installed and the Gemma model is downloaded:
```bash
ollama pull gemma3:27b-it-q8_0
```

5. Run the application:
```bash
python main.py
```

## How It Works

1. **User Input**: The user types a message.
2. **Context Management**: The message is added to the conversation history.
3. **LLM Processing**: The entire conversation history is sent to Gemma 3 27B.
4. **Response Generation**: The AI generates a response with an emotion tag.
5. **Emotion Processing**: The emotion is extracted and sent to the animation system.
6. **Animation**: The character's animation changes based on the detected emotion.
7. **Speech Synthesis**: The text response is converted to speech.
8. **Context Optimization**: If the conversation gets too long, it's automatically summarized to maintain memory while staying within token limits.

## Emotions and Animations

The system supports the following emotions, each with a corresponding animation:
- excited
- evil
- embarrassed
- annoyed
- curious
- triumphant
- sad
- neutral

## License

[Your license information here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.