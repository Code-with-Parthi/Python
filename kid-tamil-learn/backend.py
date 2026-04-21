"""
Tamil Learning App - Flask Backend with Multiple TTS Engines
This enables professional-quality speech synthesis

Supported TTS Engines:
1. pyttsx3 - Offline, open-source (RECOMMENDED for Python 3.12+)
2. Google Cloud TTS - Professional quality (via API)
3. Festival - System TTS (Linux)
4. espeak - Lightweight offline (Linux/macOS)

Installation:
pip install flask flask-cors pyttsx3

Note: Coqui TTS is incompatible with Python 3.12+
Use pyttsx3 instead for Python 3.12+

Usage:
1. python backend.py
2. Access: http://localhost:5001/api/speak
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import io
import base64
import os
import subprocess
import sys
import tempfile

app = Flask(__name__)
CORS(app)

# Python version check
PYTHON_VERSION = sys.version_info
print(f"🐍 Python {PYTHON_VERSION.major}.{PYTHON_VERSION.minor}.{PYTHON_VERSION.micro} detected")

# Try to import optional TTS libraries
TTS_AVAILABLE = {}

# pyttsx3 - Works with all Python versions including 3.14
try:
    import pyttsx3
    TTS_AVAILABLE['pyttsx3'] = True
    print("✅ pyttsx3: Available")
except ImportError as e:
    TTS_AVAILABLE['pyttsx3'] = False
    print(f"❌ pyttsx3: Not installed ({e})")

# Coqui TTS - NOT compatible with Python 3.12+
if PYTHON_VERSION.major >= 3 and PYTHON_VERSION.minor >= 12:
    TTS_AVAILABLE['coqui'] = False
    print("⚠️  Coqui TTS: Skipped (incompatible with Python 3.12+)")
else:
    try:
        from TTS.api import TTS as CoquiTTS
        TTS_AVAILABLE['coqui'] = True
        print("✅ Coqui TTS: Available")
    except (ImportError, AttributeError) as e:
        TTS_AVAILABLE['coqui'] = False
        print(f"❌ Coqui TTS: Not available ({type(e).__name__})")

# Google Cloud TTS - Works with all Python versions
try:
    from google.cloud import texttospeech
    TTS_AVAILABLE['google'] = True
    print("✅ Google Cloud TTS: Available")
except ImportError:
    TTS_AVAILABLE['google'] = False
    print("❌ Google Cloud TTS: Not installed")


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "2.1",
        "python_version": f"{PYTHON_VERSION.major}.{PYTHON_VERSION.minor}.{PYTHON_VERSION.micro}",
        "tts_engines": TTS_AVAILABLE
    })


@app.route('/api/speak', methods=['POST'])
def speak():
    """
    Text-to-Speech endpoint with automatic engine selection
    
    Request body:
    {
        "text": "தமிழ்",
        "lang": "ta",
        "speed": 0.9,
        "engine": "auto"  # or "pyttsx3", "coqui", "google"
    }
    """
    try:
        data = request.json
        text = data.get("text", "")
        lang = data.get("lang", "ta")
        speed = data.get("speed", 1.0)
        engine = data.get("engine", "auto")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        audio_data = None
        used_engine = None

        # Try specified engine first
        if engine == "auto":
            # Auto-select best available
            if TTS_AVAILABLE['pyttsx3']:
                audio_data, used_engine = speak_with_pyttsx3(text, lang, speed)
            elif TTS_AVAILABLE['coqui']:
                audio_data, used_engine = speak_with_coqui(text, lang)
            else:
                return jsonify({"error": "No TTS engine available. Install pyttsx3: pip install pyttsx3"}), 500
        elif engine == "pyttsx3":
            audio_data, used_engine = speak_with_pyttsx3(text, lang, speed)
        elif engine == "coqui":
            if PYTHON_VERSION.major >= 3 and PYTHON_VERSION.minor >= 12:
                return jsonify({"error": "Coqui TTS not compatible with Python 3.12+. Use pyttsx3 instead."}), 400
            audio_data, used_engine = speak_with_coqui(text, lang)
        elif engine == "google":
            audio_data, used_engine = speak_with_google(text, lang, speed)
        else:
            return jsonify({"error": f"Unknown engine: {engine}"}), 400

        if audio_data:
            return jsonify({
                "success": True,
                "audio": base64.b64encode(audio_data).decode(),
                "engine": used_engine,
                "text": text
            })
        else:
            return jsonify({"error": "Failed to generate audio"}), 500

    except Exception as e:
        print(f"Error in /api/speak: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


def speak_with_pyttsx3(text, lang="ta", speed=1.0):
    """
    pyttsx3 - Offline, open-source TTS
    Works on Windows, macOS, Linux
    Compatible with Python 3.6+
    Best for: Reliable offline speech
    """
    try:
        import pyttsx3
        engine = pyttsx3.init()
        
        # Set language (Tamil)
        engine.setProperty('rate', int(150 * speed))
        engine.setProperty('volume', 1.0)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            output_path = f.name
        
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        engine.stop()
        
        # Read and return
        with open(output_path, 'rb') as f:
            audio_data = f.read()
        
        # Clean up
        try:
            os.unlink(output_path)
        except:
            pass
        
        return audio_data, 'pyttsx3'
    except Exception as e:
        print(f"pyttsx3 error: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def speak_with_coqui(text, lang="ta"):
    """
    Coqui TTS - High quality, open-source
    Installation: pip install TTS
    ⚠️  NOT compatible with Python 3.12+
    Best for: High quality, offline (Python <3.12 only)
    """
    try:
        # Check Python version first
        if sys.version_info.major >= 3 and sys.version_info.minor >= 12:
            return None, None
        
        from TTS.api import TTS
        import torch
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        tts = TTS(model_name="glow-tts", gpu=device=="cuda")
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            output_path = f.name
        
        tts.tts_to_file(text=text, file_path=output_path)
        
        with open(output_path, 'rb') as f:
            audio_data = f.read()
        
        try:
            os.unlink(output_path)
        except:
            pass
        
        return audio_data, 'coqui'
    except Exception as e:
        print(f"Coqui TTS error: {e}")
        return None, None


def speak_with_google(text, lang="ta", speed=1.0):
    """
    Google Cloud Text-to-Speech - Professional quality
    Setup:
    1. Create Google Cloud project
    2. Enable Text-to-Speech API
    3. Create service account
    4. Set GOOGLE_APPLICATION_CREDENTIALS env var
    
    Best for: Production, professional quality
    Cost: Pay per request (very cheap)
    """
    try:
        from google.cloud import texttospeech
        
        client = texttospeech.TextToSpeechClient()
        
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ta-IN",
            name="ta-IN-Standard-A",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=speed
        )
        
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        return response.audio_content, 'google'
    except Exception as e:
        print(f"Google TTS error: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def speak_with_espeak(text, lang="ta", speed=1.0):
    """
    eSpeak - Lightweight, system TTS
    Installation: apt-get install espeak (Linux)
    Best for: Lightweight, offline
    """
    try:
        import subprocess
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            output_path = f.name
        
        # Use espeak with Tamil support
        speed_val = int(150 / speed)
        cmd = ['espeak', '-v', f'{lang}', '-s', str(speed_val), '-w', output_path, text]
        subprocess.run(cmd, check=True, capture_output=True)
        
        with open(output_path, 'rb') as f:
            audio_data = f.read()
        
        try:
            os.unlink(output_path)
        except:
            pass
        
        return audio_data, 'espeak'
    except Exception as e:
        print(f"eSpeak error: {e}")
        return None, None


@app.route('/api/tts-engines', methods=['GET'])
def list_tts_engines():
    """List available TTS engines and their status"""
    return jsonify({
        "available": TTS_AVAILABLE,
        "python_version": f"{PYTHON_VERSION.major}.{PYTHON_VERSION.minor}.{PYTHON_VERSION.micro}",
        "default": "pyttsx3" if TTS_AVAILABLE['pyttsx3'] else "coqui" if TTS_AVAILABLE['coqui'] else "none",
        "notes": {
            "coqui": "Not compatible with Python 3.12+. Use pyttsx3 instead.",
            "pyttsx3": "Works with all Python versions. Recommended for Python 3.14."
        }
    })


# CORS middleware
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🇹🇷 Tamil Learning Backend - TTS Server v2.1")
    print("="*60)
    print(f"\n📊 Python Version: {PYTHON_VERSION.major}.{PYTHON_VERSION.minor}.{PYTHON_VERSION.micro}")
    print("\n📊 Available TTS Engines:")
    for engine, available in TTS_AVAILABLE.items():
        status = "✅ Available" if available else "❌ Not installed"
        print(f"   {engine:15} {status}")
    
    if not any(TTS_AVAILABLE.values()):
        print("\n⚠️  WARNING: No TTS engines available!")
        print("   Install with: pip install pyttsx3")
    
    print("\n🚀 Starting server...")
    print("   Health check: http://localhost:5001/health")
    print("   TTS engines: http://localhost:5001/api/tts-engines")
    print("   API endpoint: http://localhost:5001/api/speak")
    print("\n" + "="*60 + "\n")
    
    try:
        app.run(debug=True, port=5001, host='0.0.0.0')
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
