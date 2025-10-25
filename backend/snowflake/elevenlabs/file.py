from dotenv import load_dotenv
import os
import elevenlabs

# Load environment variables from .env file
load_dotenv()

# Retrieve the ElevenLabs API key from the .env file
api_key = os.getenv("ELEVENLABS_API_KEY")
if not api_key:
    raise ValueError("ELEVENLABS_API_KEY not found in .env file")

# Initialize the ElevenLabs API client
client = elevenlabs.Client(api_key)

# Define the text to convert to speech
text_to_speech = "Hello, this is a test of the ElevenLabs text-to-speech API."

# Choose a voice (you can list available voices using client.list_voices())
voice_id = "your_voice_id_here"  # Replace with a valid voice ID

# Convert text to speech
try:
    audio = client.text_to_speech(text=text_to_speech, voice_id=voice_id)
    
    # Save the audio to a file
    with open("output_audio.mp3", "wb") as audio_file:
        audio_file.write(audio)
    print("Audio file saved as output_audio.mp3")
except Exception as e:
    print(f"An error occurred: {e}")