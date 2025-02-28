import time
import os
import sys
from pathlib import Path
import re
import json

def format_emotion_data(line):
    """Format emotion-related log entries for better readability"""
    try:
        # Extract timestamp and message
        timestamp = line[:19]  # Extract timestamp format: "2025-02-28 11:01:31"
        message = line[26:]    # Skip " - INFO - " or " - ERROR - "

        # Format different types of emotion log entries
        if "Face detected - Dominant emotion:" in message:
            # Extract emotion and confidence
            match = re.search(r"emotion: (\w+) \(confidence: ([\d.]+)\)", message)
            if match:
                emotion, confidence = match.groups()
                return f"\n{timestamp} 😊 EMOTION DETECTED:\n" \
                       f"  Primary: {emotion.upper()} ({float(confidence)*100:.1f}%)\n"
            
        elif "All emotion scores:" in message:
            return "  Detailed Scores:"
            
        elif message.strip().startswith(("happy:", "sad:", "angry:", "neutral:", "surprised:", "fear:", "disgust:")):
            # Format individual emotion scores
            emotion, score = message.strip().split(": ")
            score = float(score)
            # Create a visual bar using Unicode blocks
            bar = "█" * int(score * 20)  # Scale to 20 characters
            return f"    {emotion:10} {score*100:5.1f}% |{bar}"
            
        elif "Using detected emotion:" in message:
            emotion = message.split(": ")[1]
            return f"  ✓ CONFIRMED: Using {emotion}\n"
            
        elif "Low confidence" in message:
            match = re.search(r"confidence \(([\d.]+)\) - Using previous emotion: (\w+)", message)
            if match:
                conf, prev = match.groups()
                return f"  ⚠ LOW CONFIDENCE: Falling back to previous emotion ({prev})\n"
            
        elif "Error in emotion detection:" in message:
            error = message.split(": ")[1]
            return f"\n{timestamp} ❌ ERROR: {error}\n"
            
        elif "Failed to decode image" in message:
            return f"\n{timestamp} ❌ ERROR: Failed to decode image\n"
            
        elif "Processing image for face detection" in message:
            return f"\n{timestamp} 🔍 Processing new image...\n"
            
        return None  # Skip other log entries
        
    except Exception as e:
        return f"Error formatting log: {str(e)}\n"

def tail_log(file_path):
    """Monitor and prettify face detection logs"""
    try:
        with open(file_path, 'r') as file:
            # Go to the end of the file
            file.seek(0, 2)
            
            # Print header
            print("\n=== WhisperWell Face Detection Monitor ===")
            print("Monitoring facial expressions and emotions in real-time")
            print("Press Ctrl+C to exit")
            print("=" * 45 + "\n")
            
            while True:
                line = file.readline()
                if line:
                    formatted = format_emotion_data(line.strip())
                    if formatted:
                        print(formatted, end='', flush=True)
                else:
                    time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\nStopping emotion monitor...")
    except FileNotFoundError:
        print(f"Log file not found: {file_path}")
        print("Make sure the application has run and generated logs first")

if __name__ == "__main__":
    # Make sure the script works whether run from backend/ or backend/dev_loggers/
    backend_dir = Path(__file__).parent.parent
    log_file = backend_dir / 'logs' / 'face_detection.log'
    tail_log(str(log_file)) 