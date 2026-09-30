# Voice Assistant

A hands-free, Python-powered voice assistant designed for macOS that listens to microphone input, transcribes speech, invokes system automation tools, queries high-speed LLMs (Groq / Gemini), and speaks responses aloud via local TTS.

Available as both a **global Terminal CLI command (`whisper`)** and a **native macOS Menu Bar app (`whisper-bar`)**.

---

## Features

- **Keyboard-Activated Hotkey Mode (`CTRL + SPACE`)**: Trigger microphone recording from any application with state machine tracking (`IDLE`, `LISTENING`, `PROCESSING`, `SPEAKING`).
- **Global Terminal Command (`whisper`)**: Start the voice assistant from any directory in your terminal.
- **Native macOS Menu Bar App (`whisper-bar`)**: Sits in your top menu bar with live visual status icons (`🎙️` listening, `🧠` transcribing, `🔊` speaking, `⏸️` paused) and pause/resume controls.
- **macOS System Automation Tools**:
  - **App Controls**: Open and close any installed Mac application (`open_app`, `close_app`).
  - **Browser Automation**: Open URLs in default browser (`open_website`).
  - **Apple Music Control**: Play/pause, next/previous tracks, play specific songs and albums (`play_music`, `play_song`, `play_album`).
- **Real-Time Voice Pipeline**:
  - WebRTC VAD voice activity capture with silence detection.
  - Offline, high-accuracy STT via Faster-Whisper.
  - Groq primary model (`openai/gpt-oss-120b`) with automatic Gemini (`gemini-3.6-flash`) fallback.
  - Local low-latency voice synthesis via Pocket-TTS.

---

## Project Structure

```text
├── whisper                       # Global CLI executable entry point
├── run_gui.py                    # Menu Bar app launcher
├── app/
│   ├── audio/
│   │   ├── input.py              # Microphone capture & WebRTC VAD
│   │   └── microphone.py         # Microphone module alias
│   ├── gui/
│   │   └── menu_bar.py           # Native macOS Status Bar app (rumps)
│   ├── llm/
│   │   └── llm.py                # Groq & Gemini LLM integration with tool calling
│   ├── stt/
│   │   └── whisper.py            # Faster-Whisper STT
│   ├── tools/
│   │   ├── browser_automation.py # Browser open URL tool
│   │   ├── macos.py              # Open/Close macOS apps via osascript
│   │   └── media.py              # Apple Music AppleScript controls
│   └── tts/
│       └── tts.py                # Pocket-TTS audio generation & playback
├── requirements.txt              # Project dependencies
└── README.md
```

---

## Requirements

- macOS (Apple Silicon or Intel)
- Python 3.10+
- Microphone & Speaker access
- API Keys:
  - Groq API Key
  - Google Gemini API Key

---

## Setup & Configuration

1. **Install dependencies:**

   ```bash
   pip3 install -r requirements.txt pocket-tts langchain langchain-groq langchain-google-genai rumps
   ```

2. **Configure API Keys:**

   Create a `.env` file in the project root:

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Global CLI Setup (already configured):**

   The commands are linked into `~/.local/bin`, which is on your `$PATH`:
   - `whisper` ➔ Terminal voice assistant
   - `whisper-bar` ➔ macOS Menu Bar app

---

## Running the Assistant

### Option 1: Terminal Mode (`whisper`)

Run from **any directory** in your terminal:

```bash
whisper
```

* Speak into your microphone.
* Say **`exit`** or press `Ctrl + C` to stop.

---

### Option 2: Native Menu Bar App (`whisper-bar`)

Run in the background:

```bash
whisper-bar &
```

* A **`🎙️`** icon will appear in your top macOS menu bar.
* **Status Icons:**
  - `🎙️` — Ready & Listening
  - `🧠` — Transcribing / Thinking
  - `🔊` — Speaking response
  - `⏸️` — Paused
* **Menu Controls:** Click the icon to Pause/Resume, view the last query heard, open the project folder, or Quit.



---

## Example Voice Commands

| What You Say | Assistant Action |
| :--- | :--- |
| *"Open Safari"* | Launches Safari on your Mac |
| *"Close System Settings"* | Closes System Settings |
| *"Play music"* | Resumes playback in Apple Music |
| *"Play the album Abbey Road"* | Searches and plays Abbey Road in Apple Music |
| *"Open github.com"* | Opens the website in your default browser |
| *"What is the capital of France?"* | Streams conversational answer aloud |
| *"Exit"* | Stops the assistant |

---

## License

This project is provided as-is for personal experimentation and macOS automation.
