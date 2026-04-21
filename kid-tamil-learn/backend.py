"""
Tamil Learning App - Optional Flask Backend
This enables dynamic LLM-powered content generation
Requires: Flask, Ollama (or other local LLM)

Usage:
1. Install: pip install flask flask-cors
2. Ensure Ollama is running locally
3. Run: python backend.py
4. Access: http://localhost:5000
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import subprocess
import os

app = Flask(__name__)
CORS(app)

# Configuration
OLLAMA_MODEL = "llama2"  # or mistral, neural-chat, etc.
OLLAMA_API = "http://localhost:11434/api/generate"

# Tamil learning vocabulary
tamil_vocab = {
    "vowels": ["அ", "ஆ", "இ", "ஈ", "உ", "ஊ", "எ", "ஏ", "ஐ", "ஒ", "ஓ", "ஔ"],
    "consonants": ["க", "ங", "ச", "ஞ", "ட", "ண", "த", "ந", "ப", "ம", "ய", "ர", "ல", "வ", "ழ", "ள", "ற", "ன"],
    "common_words": ["அம்மா", "அப்பா", "நீர்", "உணவு", "பூ", "பக்ஷி", "பூனை", "குதிரை", "மரம்", "சூரியன்"]
}


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "version": "1.0"})


@app.route('/api/generate-lesson', methods=['POST'])
def generate_lesson():
    """
    Generate a Tamil lesson using LLM
    
    Request body:
    {
        "level": "beginner",
        "type": "vowels|consonants|words",
        "count": 5
    }
    """
    try:
        data = request.json
        lesson_type = data.get("type", "words")
        level = data.get("level", "beginner")
        count = data.get("count", 5)
        
        prompt = f"""
        Create {count} simple Tamil {lesson_type} for {level} learners.
        Format as JSON with this structure:
        [
            {{"word": "தமிழ்_word", "meaning": "english_meaning", "example": "use_in_sentence", "emoji": "related_emoji"}}
        ]
        
        Requirements:
        - Use only common, child-friendly words
        - Include emoji that matches the word
        - Sentences should be very simple
        - No complex grammar
        """
        
        # Generate using Ollama
        response = generate_with_ollama(prompt)
        
        # Parse response
        lesson_data = parse_llm_response(response)
        
        return jsonify({
            "success": True,
            "lesson": lesson_data
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/generate-quiz', methods=['POST'])
def generate_quiz():
    """
    Generate a quiz using LLM
    
    Request body:
    {
        "topic": "family words",
        "difficulty": "easy|medium|hard"
    }
    """
    try:
        data = request.json
        topic = data.get("topic", "Tamil words")
        difficulty = data.get("difficulty", "easy")
        
        prompt = f"""
        Create a simple Tamil learning quiz about: {topic}
        Difficulty: {difficulty}
        
        Format as JSON:
        {{
            "question": "What is the Tamil word for X?",
            "options": ["தமிழ்_word1", "தமிழ்_word2", "தமிழ்_word3", "தமிழ்_word4"],
            "correct": 0,
            "explanation": "brief explanation"
        }}
        
        Generate 5 questions. Only use kid-friendly vocabulary.
        """
        
        response = generate_with_ollama(prompt)
        quiz_data = parse_llm_response(response)
        
        return jsonify({
            "success": True,
            "quiz": quiz_data
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/translate', methods=['POST'])
def translate():
    """
    Translate English to Tamil using LLM
    
    Request body:
    {
        "text": "hello",
        "target": "ta"
    }
    """
    try:
        data = request.json
        text = data.get("text", "")
        
        prompt = f"""
        Translate to Tamil: "{text}"
        Respond with only the Tamil word/phrase, nothing else.
        Format: word|pronunciation|meaning
        """
        
        response = generate_with_ollama(prompt).strip()
        
        return jsonify({
            "success": True,
            "original": text,
            "tamil": response
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/adjust-difficulty', methods=['POST'])
def adjust_difficulty():
    """
    Adjust learning difficulty based on performance
    
    Request body:
    {
        "current_level": 1,
        "score": 85,
        "attempts": 5
    }
    """
    try:
        data = request.json
        score = data.get("score", 0)
        level = data.get("current_level", 1)
        
        # Simple logic: adjust if score > 80%
        new_level = level + 1 if score > 80 else level
        
        prompt = f"""
        Child is at Tamil learning level {new_level} with {score}% score.
        Suggest next steps: 
        - What to practice
        - Recommended activity
        - Motivational message
        
        Keep response short and encouraging.
        """
        
        suggestion = generate_with_ollama(prompt)
        
        return jsonify({
            "success": True,
            "new_level": new_level,
            "suggestion": suggestion,
            "next_lesson": tamil_vocab[["vowels", "consonants", "common_words"][min(new_level % 3, 2)]]
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/story', methods=['GET'])
def get_story():
    """
    Generate a simple Tamil story for kids
    """
    try:
        prompt = """
        Write a 5-sentence simple Tamil story for kids (age 5-8).
        Use only basic Tamil words (animals, family, nature).
        Format:
        {
            "title": "story_title",
            "lines": ["line1", "line2", "line3", "line4", "line5"],
            "moral": "simple moral"
        }
        """
        
        story = generate_with_ollama(prompt)
        parsed = parse_llm_response(story)
        
        return jsonify({
            "success": True,
            "story": parsed
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


def generate_with_ollama(prompt):
    """
    Call Ollama API to generate content
    Make sure Ollama is running: ollama serve
    """
    try:
        # Use ollama CLI if API not available
        result = subprocess.run(
            ['ollama', 'run', OLLAMA_MODEL, prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            raise Exception(f"Ollama error: {result.stderr}")
    
    except FileNotFoundError:
        # Fallama not installed
        return json.dumps({
            "error": "Ollama not found. Install from https://ollama.ai",
            "fallback": "Using pre-generated content"
        })


def parse_llm_response(response):
    """
    Try to parse LLM response as JSON
    Falls back to text if parsing fails
    """
    try:
        # Try to extract JSON from response
        start = response.find('[')
        end = response.rfind(']') + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
        
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except json.JSONDecodeError:
        pass
    
    # Return as is if not JSON
    return {"content": response}


@app.route('/api/vocabulary', methods=['GET'])
def get_vocabulary():
    """Get static vocabulary data"""
    return jsonify({
        "success": True,
        "vocabulary": tamil_vocab
    })


# CORS middleware
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response


if __name__ == '__main__':
    print("🇹🇷 Tamil Learning Backend Server")
    print("=" * 40)
    print("Make sure Ollama is running:")
    print("  ollama serve")
    print("\nThen visit: http://localhost:5000")
    print("=" * 40)
    
    app.run(debug=True, port=5000, host='0.0.0.0')
