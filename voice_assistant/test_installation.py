"""
Test script to verify voice assistant installation
Run this to check if all dependencies are working
"""

import sys

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing module imports...\n")
    
    modules = {
        'speech_recognition': 'Speech Recognition',
        'pyttsx3': 'Text-to-Speech',
        'psutil': 'System Monitoring',
        'anthropic': 'Claude API (optional)',
        'win32api': 'Windows API',
        'PIL': 'Image Processing (Pillow)'
    }
    
    results = {}
    for module, name in modules.items():
        try:
            __import__(module)
            results[name] = '✓ OK'
            print(f"✓ {name:30} OK")
        except ImportError as e:
            results[name] = f'✗ MISSING'
            print(f"✗ {name:30} MISSING - {str(e)}")
    
    return all('OK' in v for v in results.values())

def test_microphone():
    """Test microphone access"""
    print("\n\nTesting microphone access...")
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print("✓ Microphone access OK")
        print(f"  Available microphones: {sr.Microphone.list_microphone_names()[:3]}")
        return True
    except Exception as e:
        print(f"✗ Microphone test FAILED: {e}")
        return False

def test_tts():
    """Test text-to-speech"""
    print("\n\nTesting text-to-speech...")
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        print(f"✓ TTS engine OK")
        print(f"  Available voices: {len(voices)}")
        return True
    except Exception as e:
        print(f"✗ TTS test FAILED: {e}")
        return False

def test_system_info():
    """Test system monitoring"""
    print("\n\nTesting system monitoring...")
    try:
        import psutil
        
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        battery = psutil.sensors_battery()
        
        print("✓ System monitoring OK")
        print(f"  CPU Usage: {cpu}%")
        print(f"  Memory Usage: {memory.percent}%")
        if battery:
            print(f"  Battery: {battery.percent}%")
        return True
    except Exception as e:
        print(f"✗ System monitoring FAILED: {e}")
        return False

def test_config():
    """Test configuration file"""
    print("\n\nTesting configuration...")
    try:
        import json
        import os
        
        config_path = "configs/config.json"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            print("✓ Config file OK")
            print(f"  Wake word: {config.get('wake_word', 'not set')}")
            print(f"  API key configured: {'Yes' if config.get('anthropic_api_key') else 'No'}")
            return True
        else:
            print("✗ Config file not found")
            return False
    except Exception as e:
        print(f"✗ Config test FAILED: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Voice Assistant Installation Test")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_microphone,
        test_tts,
        test_system_info,
        test_config
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"Test error: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✓ All tests passed! Voice assistant is ready to use.")
        print("\nRun: python enhanced_main.py")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        print("\nCommon fixes:")
        print("  - Install missing modules: pip install -r requirements.txt")
        print("  - For PyAudio issues, see README.md")
        print("  - Check microphone permissions in Windows settings")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
