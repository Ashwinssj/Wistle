# Whistle Assistant Mobile UI (Kivy)

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty
import threading
import time

from whistle_assistant import VoiceAssistant, AssistantConfig

KV = '''
<ChatBubble>:
    orientation: 'horizontal'
    size_hint_y: None
    height: self.minimum_height
    padding: 10, 5
    
    Label:
        id: bubble_label
        text: root.message
        size_hint_x: 0.8
        text_size: self.width, None
        height: self.texture_size[1] + 20
        halign: 'left' if not root.is_user else 'right'
        valign: 'middle'
        color: 1, 1, 1, 1
        canvas.before:
            Color:
                rgba: (0.2, 0.6, 1, 1) if root.is_user else (0.3, 0.3, 0.3, 1)
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [15, 15, 15, 15] if not root.is_user else [15, 15, 15, 15]

<AssistantScreen>:
    orientation: 'vertical'
    
    BoxLayout:
        size_hint_y: None
        height: 60
        padding: 10
        canvas.before:
            Color:
                rgba: 0.15, 0.15, 0.2, 1
            Rectangle:
                pos: self.pos
                size: self.size
        
        Label:
            text: '🎤 Whistle Assistant'
            font_size: 22
            bold: True
            color: 1, 1, 1, 1
        
        Label:
            id: status_label
            text: root.status_text
            font_size: 16
            color: 0.7, 1, 0.7, 1
            size_hint_x: 0.4
            halign: 'right'
            text_size: self.size

    ScrollView:
        id: chat_scroll
        do_scroll_x: False
        
        BoxLayout:
            id: chat_container
            orientation: 'vertical'
            size_hint_y: None
            height: self.minimum_height
            padding: 10
            spacing: 5

    BoxLayout:
        size_hint_y: None
        height: 80
        padding: 10
        spacing: 10
        canvas.before:
            Color:
                rgba: 0.1, 0.1, 0.15, 1
            Rectangle:
                pos: self.pos
                size: self.size
        
        Button:
            id: mic_button
            text: '🎤 Tap to Talk' if not root.listening else '🔴 Listening...'
            font_size: 18
            background_color: (0.2, 0.7, 0.3, 1) if not root.listening else (0.8, 0.2, 0.2, 1)
            on_press: root.toggle_listening()
            disabled: not root.ready
        
        Button:
            text: '⚙️ Settings'
            font_size: 18
            background_color: 0.3, 0.3, 0.4, 1
            size_hint_x: 0.3
            on_press: root.open_settings()

<SettingsScreen>:
    orientation: 'vertical'
    padding: 20
    spacing: 15
    
    Label:
        text: 'Settings'
        font_size: 28
        bold: True
        size_hint_y: None
        height: 50
        color: 1, 1, 1, 1
    
    BoxLayout:
        orientation: 'vertical'
        spacing: 10
        size_hint_y: None
        height: self.minimum_height
        
        Label:
            text: 'Wake Words (one per line):'
            size_hint_y: None
            height: 30
            color: 0.8, 0.8, 0.8, 1
        
        TextInput:
            id: wake_words_input
            text: '\\n'.join(root.wake_words)
            multiline: True
            size_hint_y: None
            height: 150
            background_color: 0.2, 0.2, 0.25, 1
            foreground_color: 1, 1, 1, 1
        
        Label:
            text: 'Language:'
            size_hint_y: None
            height: 30
            color: 0.8, 0.8, 0.8, 1
        
        Spinner:
            id: language_spinner
            text: root.language or 'Auto-detect'
            values: ['Auto-detect', 'en', 'de', 'fr', 'es', 'it', 'nl', 'pl']
            size_hint_y: None
            height: 50
            background_color: 0.2, 0.2, 0.25, 1
        
        Button:
            text: 'Save Settings'
            size_hint_y: None
            height: 50
            background_color: 0.2, 0.6, 1, 1
            on_press: root.save_settings()
        
        Button:
            text: 'Back to Assistant'
            size_hint_y: None
            height: 50
            background_color: 0.4, 0.4, 0.5, 1
            on_press: root.go_back()
'''

from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner

Builder.load_string(KV)


class ChatBubble(BoxLayout):
    message = StringProperty('')
    is_user = BooleanProperty(False)


class AssistantScreen(BoxLayout):
    status_text = StringProperty('Ready — Tap mic to start')
    listening = BooleanProperty(False)
    ready = BooleanProperty(True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.assistant = None
        self.assistant_thread = None
        self._init_assistant()
    
    def _init_assistant(self):
        """Initialize the voice assistant in background."""
        def init():
            try:
                config = AssistantConfig()
                self.assistant = VoiceAssistant(config)
                self.assistant._speak = self._mobile_speak
                Clock.schedule_once(lambda dt: setattr(self, 'ready', True))
                Clock.schedule_once(lambda dt: setattr(self, 'status_text', 'Ready — Tap mic to start'))
            except Exception as e:
                Clock.schedule_once(lambda dt: self._add_message(f"Error: {e}", is_user=False))
        
        threading.Thread(target=init, daemon=True).start()
    
    def _mobile_speak(self, text):
        """Override TTS for mobile - use plyer or print."""
        try:
            from plyer import tts
            tts.speak(text)
        except Exception:
            print(f"🔊 {text}")
    
    def _add_message(self, message, is_user=False):
        """Add a message to the chat."""
        bubble = ChatBubble(message=message, is_user=is_user)
        self.ids.chat_container.add_widget(bubble)
        # Auto-scroll to bottom
        Clock.schedule_once(lambda dt: setattr(self.ids.chat_scroll, 'scroll_y', 0), 0.1)
    
    def toggle_listening(self):
        """Start/stop listening for a single command."""
        if not self.ready or not self.assistant:
            return
        
        if not self.listening:
            self.listening = True
            self.status_text = '🔴 Listening...'
            self._add_message('', is_user=True)  # Placeholder
            threading.Thread(target=self._listen_once, daemon=True).start()
        else:
            self.listening = False
            self.status_text = 'Processing...'
    
    def _listen_once(self):
        """Record audio, transcribe, process, respond."""
        try:
            import sounddevice as sd
            import numpy as np
            
            SAMPLE_RATE = 16000
            DURATION = 5  # seconds
            
            # Record
            recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype=np.float32)
            sd.wait()
            audio = recording.flatten()
            
            # Transcribe
            result = self.assistant.whistle.transcribe(audio)
            text = result.get("text", "").strip()
            
            Clock.schedule_once(lambda dt: self._on_transcribed(text))
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self._on_error(str(e)))
    
    def _on_transcribed(self, text):
        """Handle transcribed text."""
        self.listening = False
        
        if not text:
            self._add_message("(no speech detected)", is_user=False)
            self.status_text = 'Ready — Tap mic to start'
            return
        
        # Update the placeholder user message
        if self.ids.chat_container.children:
            self.ids.chat_container.children[-1].message = text
        
        # Process with Needle
        self.status_text = 'Thinking...'
        threading.Thread(target=self._process_command, args=(text,), daemon=True).start()
    
    def _process_command(self, text):
        """Process command with Needle."""
        try:
            response = self.assistant.agent.run(text)
            Clock.schedule_once(lambda dt: self._on_response(response, text))
        except Exception as e:
            Clock.schedule_once(lambda dt: self._on_error(str(e)))
    
    def _on_response(self, response, original_text):
        """Handle Needle response."""
        function_calls = response.get("function_calls", [])
        reasoning = response.get("reasoning", "")
        
        if function_calls:
            for call in function_calls:
                func_name = call.get("name")
                args = call.get("arguments", {})
                tool_func = self.assistant.agent._functions.get(func_name)
                if tool_func:
                    try:
                        result = tool_func(**args)
                        msg = result.get("message", f"Executed {func_name}")
                        self._add_message(msg, is_user=False)
                        self._mobile_speak(msg)
                    except Exception as e:
                        self._add_message(f"Error: {e}", is_user=False)
        elif reasoning:
            self._add_message(reasoning, is_user=False)
            self._mobile_speak(reasoning)
        else:
            self._add_message("I didn't understand that.", is_user=False)
        
        self.status_text = 'Ready — Tap mic to start'
    
    def _on_error(self, error):
        self.listening = False
        self._add_message(f"Error: {error}", is_user=False)
        self.status_text = 'Ready — Tap mic to start'
    
    def open_settings(self):
        app = App.get_running_app()
        app.root.current = 'settings'
    
    def go_back(self):
        app = App.get_running_app()
        app.root.current = 'assistant'


class SettingsScreen(BoxLayout):
    wake_words = StringProperty('hey assistant\nokay assistant\nwhistle\ncomputer')
    language = StringProperty('')
    
    def save_settings(self):
        wake_words = self.ids.wake_words_input.text.strip().split('\n')
        language = self.ids.language_spinner.text
        if language == 'Auto-detect':
            language = None
        
        # Update assistant config
        if self.parent and hasattr(self.parent, 'get_screen'):
            assistant_screen = self.parent.get_screen('assistant')
            if assistant_screen.assistant:
                assistant_screen.assistant.config.wake_words = [w.strip() for w in wake_words if w.strip()]
                assistant_screen.assistant.config.language = language
        
        self.go_back()
    
    def go_back(self):
        app = App.get_running_app()
        app.root.current = 'assistant'


class WhistleAssistantApp(App):
    def build(self):
        from kivy.uix.screenmanager import ScreenManager, Screen
        
        sm = ScreenManager()
        
        assistant_screen = AssistantScreen(name='assistant')
        settings_screen = SettingsScreen(name='settings')
        
        sm.add_widget(assistant_screen)
        sm.add_widget(settings_screen)
        
        return sm


if __name__ == '__main__':
    WhistleAssistantApp().run()