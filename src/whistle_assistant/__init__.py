"""
Offline voice assistant using Whistle ASR + Needle tool calling.
All processing happens locally on device.
"""

import os
import sys
import json
import time
import threading
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional, Callable
import queue

import needle
import sounddevice as sd
import numpy as np

# ─── Configuration ──────────────────────────────────────────────────
SAMPLE_RATE = 16000
CHUNK_DURATION = 1.0  # seconds per chunk for streaming
CHUNK_SAMPLES = int(SAMPLE_RATE * CHUNK_DURATION)
WAKE_WORDS = ["hey assistant", "okay assistant", "whistle", "computer"]
SILENCE_THRESHOLD = 0.01
SILENCE_DURATION = 1.5  # seconds of silence to end utterance

# ─── Data Structures ────────────────────────────────────────────────
@dataclass
class Reminder:
    text: str
    trigger_time: datetime
    id: str = field(default_factory=lambda: str(time.time()))

@dataclass
class AssistantConfig:
    wake_words: list[str] = field(default_factory=lambda: WAKE_WORDS)
    sample_rate: int = SAMPLE_RATE
    chunk_duration: float = CHUNK_DURATION
    silence_threshold: float = SILENCE_THRESHOLD
    silence_duration: float = SILENCE_DURATION
    language: Optional[str] = None
    keywords: list[str] = field(default_factory=list)

# ─── Tool Implementations ───────────────────────────────────────────

def open_app(app_name: str) -> dict:
    """Open an application by name."""
    system = sys.platform
    app_name_lower = app_name.lower()
    
    # Common app mappings
    app_map = {
        "browser": {"win": "start msedge", "linux": "xdg-open", "darwin": "open -a Safari"},
        "chrome": {"win": "start chrome", "linux": "google-chrome", "darwin": "open -a \"Google Chrome\""},
        "firefox": {"win": "start firefox", "linux": "firefox", "darwin": "open -a Firefox"},
        "edge": {"win": "start msedge", "linux": "microsoft-edge", "darwin": "open -a \"Microsoft Edge\""},
        "terminal": {"win": "wt", "linux": "gnome-terminal", "darwin": "open -a Terminal"},
        "cmd": {"win": "cmd", "linux": "gnome-terminal", "darwin": "open -a Terminal"},
        "powershell": {"win": "powershell", "linux": "gnome-terminal", "darwin": "open -a Terminal"},
        "notepad": {"win": "notepad", "linux": "gedit", "darwin": "open -a TextEdit"},
        "vscode": {"win": "code", "linux": "code", "darwin": "code"},
        "code": {"win": "code", "linux": "code", "darwin": "code"},
        "calculator": {"win": "calc", "linux": "gnome-calculator", "darwin": "open -a Calculator"},
        "settings": {"win": "start ms-settings:", "linux": "gnome-control-center", "darwin": "open -a \"System Settings\""},
        "explorer": {"win": "explorer", "linux": "nautilus", "darwin": "open -a Finder"},
        "finder": {"win": "explorer", "linux": "nautilus", "darwin": "open -a Finder"},
        "spotify": {"win": "start spotify", "linux": "spotify", "darwin": "open -a Spotify"},
        "discord": {"win": "start discord", "linux": "discord", "darwin": "open -a Discord"},
        "slack": {"win": "start slack", "linux": "slack", "darwin": "open -a Slack"},
    }
    
    if app_name_lower in app_map:
        cmd = app_map[app_name_lower].get(system, app_map[app_name_lower].get("linux"))
        if system == "win32":
            subprocess.Popen(cmd, shell=True)
        else:
            subprocess.Popen(cmd.split())
        return {"success": True, "message": f"Opened {app_name}"}
    
    # Try direct execution
    try:
        if system == "win32":
            subprocess.Popen(f"start {app_name}", shell=True)
        else:
            subprocess.Popen([app_name])
        return {"success": True, "message": f"Launched {app_name}"}
    except Exception as e:
        return {"success": False, "message": f"Could not open {app_name}: {e}"}

def set_reminder(text: str, minutes_from_now: int = 0, hours_from_now: int = 0, at_time: str = "") -> dict:
    """Set a reminder. Provide either minutes/hours from now, or an absolute time like '14:30'."""
    now = datetime.now()
    
    if at_time:
        try:
            hour, minute = map(int, at_time.split(":"))
            trigger = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if trigger <= now:
                trigger += timedelta(days=1)
        except ValueError:
            return {"success": False, "message": "Invalid time format. Use HH:MM (24-hour)"}
    else:
        trigger = now + timedelta(hours=hours_from_now, minutes=minutes_from_now)
    
    reminder = Reminder(text=text, trigger_time=trigger)
    
    # Store reminder (in memory for now; could persist to file)
    _reminders.append(reminder)
    
    # Schedule notification
    delay = (trigger - now).total_seconds()
    threading.Timer(delay, _notify_reminder, args=[reminder]).start()
    
    return {
        "success": True,
        "message": f"Reminder set for {trigger.strftime('%H:%M')}: {text}",
        "trigger_time": trigger.isoformat()
    }

def list_reminders() -> dict:
    """List all active reminders."""
    now = datetime.now()
    active = [r for r in _reminders if r.trigger_time > now]
    return {
        "success": True,
        "reminders": [
            {"id": r.id, "text": r.text, "time": r.trigger_time.strftime("%Y-%m-%d %H:%M")}
            for r in active
        ]
    }

def cancel_reminder(reminder_id: str) -> dict:
    """Cancel a reminder by ID."""
    global _reminders
    _reminders = [r for r in _reminders if r.id != reminder_id]
    return {"success": True, "message": "Reminder cancelled"}

def search_files(query: str, path: str = "~", max_results: int = 20) -> dict:
    """Search for files by name/content in a directory."""
    search_path = Path(path).expanduser()
    if not search_path.exists():
        return {"success": False, "message": f"Path not found: {path}"}
    
    results = []
    query_lower = query.lower()
    
    for file_path in search_path.rglob("*"):
        if len(results) >= max_results:
            break
        if file_path.is_file():
            # Match filename
            if query_lower in file_path.name.lower():
                results.append({
                    "path": str(file_path),
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    "match_type": "filename"
                })
                continue
            
            # Match content for text files (small files only)
            if file_path.stat().st_size < 1024 * 1024:  # < 1MB
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    if query_lower in content.lower():
                        results.append({
                            "path": str(file_path),
                            "name": file_path.name,
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                            "match_type": "content"
                        })
                except Exception:
                    pass
    
    return {"success": True, "results": results, "count": len(results)}

def open_file(file_path: str) -> dict:
    """Open a file with its default application."""
    path = Path(file_path).expanduser()
    if not path.exists():
        return {"success": False, "message": f"File not found: {file_path}"}
    
    system = sys.platform
    try:
        if system == "win32":
            os.startfile(str(path))
        elif system == "darwin":
            subprocess.run(["open", str(path)])
        else:
            subprocess.run(["xdg-open", str(path)])
        return {"success": True, "message": f"Opened {path.name}"}
    except Exception as e:
        return {"success": False, "message": f"Could not open file: {e}"}

def get_time() -> dict:
    """Get current date and time."""
    now = datetime.now()
    return {
        "success": True,
        "time": now.strftime("%H:%M"),
        "date": now.strftime("%A, %B %d, %Y"),
        "iso": now.isoformat()
    }

def run_command(command: str) -> dict:
    """Run a shell command (use with caution)."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "Command timed out"}
    except Exception as e:
        return {"success": False, "message": str(e)}

# ─── Reminder Storage ───────────────────────────────────────────────
_reminders: list[Reminder] = []

def _notify_reminder(reminder: Reminder):
    """Show a desktop notification for a reminder."""
    try:
        from plyer import notification
        notification.notify(
            title="⏰ Reminder",
            message=reminder.text,
            timeout=10
        )
    except Exception:
        print(f"\n⏰ REMINDER: {reminder.text}")

# ─── Voice Assistant Core ───────────────────────────────────────────

class VoiceAssistant:
    def __init__(self, config: Optional[AssistantConfig] = None):
        self.config = config or AssistantConfig()
        self.running = False
        self.audio_queue: queue.Queue = queue.Queue()
        self.stream = None
        
        # Initialize Whistle for ASR
        print("Loading Whistle ASR model...")
        self.whistle = needle.Whistle()
        print("Whistle loaded.")
        
        # Initialize Needle for tool calling
        print("Loading Needle tool-calling model...")
        self.agent = needle.Needle(
            tools=[
                open_app,
                set_reminder,
                list_reminders,
                cancel_reminder,
                search_files,
                open_file,
                get_time,
                run_command,
            ],
            system="You are a helpful voice assistant running entirely offline on the user's device. "
                   "You can open apps, set reminders, search files, and run commands. "
                   "Keep responses concise and conversational."
        )
        print("Needle loaded.")
        
        # Wake word detection state
        self.wake_word_detected = False
        self.listening_for_command = False
        self.audio_buffer = []
        self.silence_start = None

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for sounddevice input stream."""
        if status:
            print(f"Audio status: {status}")
        self.audio_queue.put(indata.copy())

    def _rms(self, audio: np.ndarray) -> float:
        """Calculate RMS energy of audio."""
        return np.sqrt(np.mean(audio**2))

    def _detect_wake_word(self, text: str) -> bool:
        """Check if wake word is in transcribed text."""
        text_lower = text.lower()
        return any(wake in text_lower for wake in self.config.wake_words)

    def _process_audio_stream(self):
        """Process streaming audio for wake word and command detection."""
        print("Listening for wake word...")
        
        while self.running:
            try:
                chunk = self.audio_queue.get(timeout=0.1)
                audio_data = chunk[:, 0] if chunk.ndim > 1 else chunk.flatten()
                
                # Simple voice activity detection
                rms = self._rms(audio_data)
                
                if rms > self.config.silence_threshold:
                    # Speech detected
                    self.audio_buffer.extend(audio_data)
                    self.silence_start = None
                else:
                    # Silence
                    if self.audio_buffer and self.silence_start is None:
                        self.silence_start = time.time()
                    elif self.silence_start and (time.time() - self.silence_start) > self.config.silence_duration:
                        # End of utterance - process it
                        if len(self.audio_buffer) > SAMPLE_RATE * 0.5:  # At least 0.5s of audio
                            self._process_utterance(np.array(self.audio_buffer, dtype=np.float32))
                        self.audio_buffer = []
                        self.silence_start = None
                        
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Audio processing error: {e}")

    def _process_utterance(self, audio: np.ndarray):
        """Transcribe and process a complete utterance."""
        try:
            # Transcribe with Whistle
            result = self.whistle.transcribe(
                audio, 
                language=self.config.language,
                keywords=self.config.keywords
            )
            text = result.get("text", "").strip()
            
            if not text:
                return
            
            print(f"Heard: {text}")
            
            if not self.wake_word_detected:
                # Check for wake word
                if self._detect_wake_word(text):
                    self.wake_word_detected = True
                    self.listening_for_command = True
                    print("🎙️ Wake word detected! Listening for command...")
                    # Play a subtle beep or visual indicator
                    self._play_beep()
                return
            
            # We're in command mode - send to Needle
            self.listening_for_command = False
            self.wake_word_detected = False
            
            # Process with Needle (tool calling)
            response = self.agent.run(text)
            self._handle_response(response, text)
            
        except Exception as e:
            print(f"Processing error: {e}")
            self.wake_word_detected = False
            self.listening_for_command = False

    def _handle_response(self, response: dict, original_text: str):
        """Handle Needle's response and execute tool calls."""
        function_calls = response.get("function_calls", [])
        reasoning = response.get("reasoning", "")
        confidence = response.get("confidence")
        
        if function_calls:
            print(f"🤖 Assistant: {reasoning}")
            for call in function_calls:
                func_name = call.get("name")
                args = call.get("arguments", {})
                print(f"  → Calling {func_name}({args})")
                
                # Execute the tool
                tool_func = self.agent._functions.get(func_name)
                if tool_func:
                    try:
                        result = tool_func(**args)
                        print(f"  ✓ Result: {result}")
                        
                        # Speak result if it has a message
                        if isinstance(result, dict) and "message" in result:
                            self._speak(result["message"])
                    except Exception as e:
                        print(f"  ✗ Error: {e}")
                        self._speak(f"Sorry, I couldn't {func_name.replace('_', ' ')}.")
                else:
                    print(f"  ✗ Unknown tool: {func_name}")
        else:
            # No tool calls - just conversational response
            if reasoning:
                print(f"🤖 Assistant: {reasoning}")
                self._speak(reasoning)
            else:
                self._speak("I didn't catch that. Could you repeat?")

    def _speak(self, text: str):
        """Text-to-speech using system TTS."""
        system = sys.platform
        try:
            if system == "win32":
                # Windows SAPI
                import subprocess
                ps_script = f'Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak("{text}")'
                subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
            elif system == "darwin":
                subprocess.run(["say", text])
            else:
                # Linux - try espeak, festival, or spd-say
                for cmd in [["espeak", text], ["spd-say", text], ["festival", "--tts"]]:
                    try:
                        subprocess.run(cmd, capture_output=True, check=True)
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
        except Exception:
            print(f"🔊 {text}")  # Fallback: print

    def _play_beep(self):
        """Play a short beep for wake word feedback."""
        try:
            # Generate a simple beep
            duration = 0.1
            freq = 880
            t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
            beep = 0.3 * np.sin(2 * np.pi * freq * t)
            sd.play(beep, SAMPLE_RATE, blocking=True)
        except Exception:
            pass

    def start(self):
        """Start the voice assistant."""
        self.running = True
        
        # Start audio input stream
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype=np.float32,
            blocksize=CHUNK_SAMPLES,
            callback=self._audio_callback
        )
        self.stream.start()
        
        # Start processing thread
        self.process_thread = threading.Thread(target=self._process_audio_stream, daemon=True)
        self.process_thread.start()
        
        print("\n🎤 Voice Assistant started!")
        print(f"Wake words: {', '.join(self.config.wake_words)}")
        print("Say a wake word to activate, then speak your command.")
        print("Press Ctrl+C to stop.\n")

    def stop(self):
        """Stop the voice assistant."""
        self.running = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
        print("\n👋 Voice Assistant stopped.")

    def run_forever(self):
        """Run until interrupted."""
        self.start()
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()


# ─── CLI Entry Point ────────────────────────────────────────────────

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Offline Voice Assistant with Whistle + Needle")
    parser.add_argument("--wake-words", nargs="+", default=WAKE_WORDS, help="Wake words to listen for")
    parser.add_argument("--language", choices=["en", "de", "fr", "es", "it", "nl", "pl"], help="Force language")
    parser.add_argument("--keywords", nargs="+", help="Keywords to bias recognition")
    parser.add_argument("--device", type=int, help="Audio input device index")
    parser.add_argument("--list-devices", action="store_true", help="List audio devices and exit")
    
    args = parser.parse_args()
    
    if args.list_devices:
        print(sd.query_devices())
        return
    
    if args.device is not None:
        sd.default.device = args.device
    
    config = AssistantConfig(
        wake_words=args.wake_words,
        language=args.language,
        keywords=args.keywords or []
    )
    
    assistant = VoiceAssistant(config)
    assistant.run_forever()


if __name__ == "__main__":
    main()