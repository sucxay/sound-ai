#!/bin/bash
# Helper script to manage Voice Assistant as an automatic macOS background daemon (like Siri)

PLIST_NAME="com.user.voiceassistant.plist"
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$PLIST_DIR/$PLIST_NAME"
PROJECT_DIR="/Users/suchayjoshi/Desktop/voice_assistant"
PYTHON_BIN="/Library/Frameworks/Python.framework/Versions/3.13/bin/python3"

generate_plist() {
    mkdir -p "$PLIST_DIR"
    cat <<EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.voiceassistant</string>

    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_BIN</string>
        <string>$PROJECT_DIR/main.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/assistant.log</string>

    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/assistant.err.log</string>
</dict>
</plist>
EOF
}

case "$1" in
    install|start)
        echo "⚙️ Setting up Voice Assistant background service..."
        generate_plist
        launchctl unload "$PLIST_PATH" 2>/dev/null
        launchctl load -w "$PLIST_PATH"
        echo "✅ Voice Assistant service started in the background!"
        echo "👉 Press CTRL + SPACE at any time (from Desktop or any app) to talk to the assistant."
        ;;
    stop)
        echo "🛑 Stopping Voice Assistant background service..."
        launchctl unload "$PLIST_PATH" 2>/dev/null
        echo "✅ Service stopped."
        ;;
    restart)
        echo "🔄 Restarting Voice Assistant..."
        launchctl unload "$PLIST_PATH" 2>/dev/null
        launchctl load -w "$PLIST_PATH"
        echo "✅ Restarted."
        ;;
    status)
        if launchctl list | grep -q "com.user.voiceassistant"; then
            echo "🟢 Voice Assistant background service is RUNNING."
            echo "PID & Exit Code:"
            launchctl list | grep "com.user.voiceassistant"
        else
            echo "🔴 Voice Assistant background service is NOT running."
        fi
        ;;
    logs)
        echo "📋 Tailing logs (Press Ctrl+C to exit)..."
        tail -f "$PROJECT_DIR/assistant.log" "$PROJECT_DIR/assistant.err.log"
        ;;
    uninstall)
        echo "🗑️ Removing Voice Assistant background service..."
        launchctl unload "$PLIST_PATH" 2>/dev/null
        rm -f "$PLIST_PATH"
        echo "✅ Service uninstalled."
        ;;
    *)
        echo "Usage: whisper-service {start|stop|restart|status|logs|uninstall}"
        exit 1
        ;;
esac
