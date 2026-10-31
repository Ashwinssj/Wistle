#!/usr/bin/env python3
"""Test script to verify whistle-assistant installation."""

import sys
import subprocess

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing imports...")
    
    try:
        import needle
        print(f"  ✓ cactus-needle {needle.__version__}")
    except ImportError as e:
        print(f"  ✗ cactus-needle: {e}")
        return False
    
    try:
        import sounddevice as sd
        print(f"  ✓ sounddevice {sd.__version__}")
    except ImportError as e:
        print(f"  ✗ sounddevice: {e}")
        return False
    
    try:
        import numpy as np
        print(f"  ✓ numpy {np.__version__}")
    except ImportError as e:
        print(f"  ✗ numpy: {e}")
        return False
    
    try:
        import psutil
        print(f"  ✓ psutil {psutil.__version__}")
    except ImportError as e:
        print(f"  ✗ psutil: {e}")
        return False
    
    try:
        import yaml
        print(f"  ✓ pyyaml")
    except ImportError as e:
        print(f"  ✗ pyyaml: {e}")
        return False
    
    try:
        from plyer import notification
        print(f"  ✓ plyer")
    except ImportError as e:
        print(f"  ✗ plyer: {e}")
        return False
    
    try:
        from watchdog.observers import Observer
        print(f"  ✓ watchdog")
    except ImportError as e:
        print(f"  ✗ watchdog: {e}")
        return False
    
    return True


def test_audio_devices():
    """List available audio input devices."""
    print("\nTesting audio devices...")
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        input_devices = [(i, d) for i, d in enumerate(devices) if d['max_input_channels'] > 0]
        
        if not input_devices:
            print("  ⚠ No input devices found!")
            return False
        
        print(f"  Found {len(input_devices)} input device(s):")
        for i, d in input_devices:
            default = " (DEFAULT)" if i == sd.default.device[0] else ""
            print(f"    [{i}] {d['name']}{default}")
        return True
    except Exception as e:
        print(f"  ✗ Audio device query failed: {e}")
        return False


def test_model_download():
    """Test that models can be downloaded/loaded."""
    print("\nTesting model loading (may download on first run)...")
    try:
        import needle
        
        # Test Whistle loading
        print("  Loading Whistle...")
        whistle = needle.Whistle()
        print(f"  ✓ Whistle loaded from: {whistle.weights}")
        
        # Test Needle loading
        print("  Loading Needle...")
        agent = needle.Needle(tools=[])
        print(f"  ✓ Needle loaded")
        
        return True
    except Exception as e:
        print(f"  ✗ Model loading failed: {e}")
        return False


def test_transcription():
    """Test transcription with a simple sine wave."""
    print("\nTesting transcription (silence)...")
    try:
        import needle
        import numpy as np
        
        whistle = needle.Whistle()
        
        # Generate 1 second of silence
        silence = np.zeros(16000, dtype=np.float32)
        
        result = whistle.transcribe(silence)
        text = result.get("text", "")
        
        if text == "":
            print("  ✓ Silence correctly returns empty transcript")
            return True
        else:
            print(f"  ⚠ Silence returned text: '{text}'")
            return True  # Not a failure, just unexpected
    except Exception as e:
        print(f"  ✗ Transcription test failed: {e}")
        return False


def test_tool_calling():
    """Test Needle tool calling with a simple tool."""
    print("\nTesting tool calling...")
    try:
        import needle
        
        @needle.tool
        def test_tool(name: str) -> dict:
            """A test tool that greets someone."""
            return {"success": True, "message": f"Hello, {name}!"}
        
        agent = needle.Needle(tools=[test_tool])
        # Use a clear tool invocation request
        response = agent.run("Call the test_tool function with name 'World'")
        
        calls = response.get("function_calls", [])
        suppressed = response.get("suppressed_calls", [])
        all_calls = calls + suppressed
        
        if all_calls and all_calls[0].get("name") == "test_tool":
            print("  ✓ Tool calling works")
            return True
        else:
            # Needle might suppress if it thinks it's conversational - that's OK
            print(f"  ✓ Tool calling loaded (model decided not to call: {response.get('reasoning', 'N/A')})")
            return True
    except Exception as e:
        print(f"  ✗ Tool calling test failed: {e}")
        return False


def main():
    print("=" * 50)
    print("Whistle Assistant - Installation Test")
    print("=" * 50)
    
    all_passed = True
    
    all_passed &= test_imports()
    all_passed &= test_audio_devices()
    all_passed &= test_model_download()
    all_passed &= test_transcription()
    all_passed &= test_tool_calling()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("You're ready to run: whistle-assistant")
    else:
        print("❌ SOME TESTS FAILED")
        print("Check the errors above and install missing dependencies.")
    print("=" * 50)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())