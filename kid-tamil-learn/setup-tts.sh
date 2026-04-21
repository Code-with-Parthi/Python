#!/bin/bash
# Quick setup scripts for Tamil Learning App - TTS Setup

echo "🇹🇷 Tamil Learning App - TTS Setup Helper"
echo "=========================================="
echo ""

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    OS="Windows"
else
    OS="Unknown"
fi

echo "Detected OS: $OS"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Menu
echo "Choose your setup option:"
echo ""
echo "1) Setup Local Backend (pyttsx3 - Offline)"
echo "2) Setup Local Backend (Coqui TTS - High Quality)"
echo "3) Setup Google Cloud TTS (Professional Quality)"
echo "4) Test Current Installation"
echo "5) Start Backend Server"
echo "6) Exit"
echo ""
read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo ""
        echo "📦 Installing pyttsx3 backend..."
        pip3 install pyttsx3 flask flask-cors
        
        if [ "$OS" = "macOS" ]; then
            echo "🍎 macOS: Installing audio support..."
            brew install portaudio 2>/dev/null || echo "⚠️ portaudio already installed"
        elif [ "$OS" = "Linux" ]; then
            echo "🐧 Linux: Installing audio support..."
            sudo apt-get install -y portaudio19-dev alsa-utils
        fi
        
        echo "✅ pyttsx3 installed successfully!"
        echo "🚀 Next: Run 'python backend.py' to start server"
        ;;
    
    2)
        echo ""
        echo "📦 Installing Coqui TTS (High Quality Neural Voice)..."
        echo "⚠️  This is large (~500MB) and may take 5-10 minutes..."
        pip3 install TTS flask flask-cors
        
        echo "✅ Coqui TTS installed successfully!"
        echo "🚀 Next: Run 'python backend.py' to start server"
        ;;
    
    3)
        echo ""
        echo "🔑 Google Cloud Text-to-Speech Setup"
        echo "======================================"
        echo ""
        echo "1. Go to: https://cloud.google.com/text-to-speech"
        echo "2. Click 'Try Free' and sign in"
        echo "3. Create a new project"
        echo "4. Enable Text-to-Speech API"
        echo "5. Create Service Account (with JSON key)"
        echo "6. Download the JSON file"
        echo "7. Set environment variable:"
        echo ""
        echo "   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/key.json"
        echo ""
        echo "8. Test with:"
        echo "   pip3 install google-cloud-texttospeech flask flask-cors"
        echo "   python backend.py"
        echo ""
        ;;
    
    4)
        echo ""
        echo "🧪 Testing current TTS installation..."
        echo ""
        python3 << 'EOF'
import sys

# Test pyttsx3
try:
    import pyttsx3
    print("✅ pyttsx3: Available")
except ImportError:
    print("❌ pyttsx3: Not installed")

# Test Coqui TTS
try:
    from TTS.api import TTS
    print("✅ Coqui TTS: Available")
except ImportError:
    print("❌ Coqui TTS: Not installed (optional)")

# Test Google Cloud
try:
    from google.cloud import texttospeech
    print("✅ Google Cloud TTS: Available")
except ImportError:
    print("❌ Google Cloud TTS: Not installed (optional)")

# Test Flask
try:
    import flask
    print("✅ Flask: Available")
except ImportError:
    print("❌ Flask: Not installed")

print("")
print("Run 'python backend.py' to start the server")
EOF
        ;;
    
    5)
        echo ""
        echo "🚀 Starting Tamil Learning Backend..."
        echo "======================================"
        echo ""
        echo "Make sure you're in the kid-tamil-learn directory:"
        echo "  cd kid-tamil-learn"
        echo ""
        python3 backend.py
        ;;
    
    6)
        echo "Goodbye! 👋"
        exit 0
        ;;
    
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "For more details, see TTS-GUIDE.md"
echo "Enjoy learning Tamil! 🇹🇷"
