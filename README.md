# Voice Assistant

A Python-based voice assistant that listens to microphone input, transcribes speech, sends the text to a language model, and speaks the response back aloud.

This project combines:
- microphone capture and voice activity detection
- speech-to-text via Faster Whisper
- LLM responses through Groq
- text-to-speech playback using a local TTS model

## Features

- Real-time microphone recording with silence detection
- Automatic speech segmentation using WebRTC VAD
- Whisper-based transcription
- Groq-powered conversational responses
- Audio playback for assistant replies
- Simple loop-based CLI interaction

## Project Structure

- [app/audio/input.py](app/audio/input.py) — microphone input and VAD-based recording logic
- [app/stt/whisper.py](app/stt/whisper.py) — speech-to-text transcription using Whisper
- [app/llm/llm.py](app/llm/llm.py) — Groq LLM integration
- [app/tts/tts.py](app/tts/tts.py) — text-to-speech generation and playback
- [run.py](run.py) — main assistant loop
- [test.py](test.py) — basic usage/test script
- [requirements.txt](requirements.txt) — Python dependencies
- [main.py](main.py) — placeholder entry point

## Requirements

- Python 3.10+
- Microphone access on your machine
- A Groq API key

## Setup

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add your Groq API key in a `.env` file in the project root:

```env
GROQ_API_KEY=your_api_key_here
```

## Run the assistant

Start the voice assistant:

```bash
python run.py
```

Then:
- speak into the microphone
- the app will transcribe your speech
- the model will generate a response
- the assistant will speak the answer back
- say `exit` to stop the program

## Notes

- This app is designed for local experimentation and development.
- Audio and model performance may vary depending on system resources and hardware.
- Some TTS and Whisper setups may require additional OS-level audio dependencies depending on your environment.

## Example flow

```text
You: Hello
Assistant: Hello! How can I help you today?
```

## License

This project is provided as-is for learning and experimentation.
