import elevenlabs
import openai
from elevenlabs.client import ElevenLabs
import os


class ElevenLabsClient:
    def __init__(self):
        self.elevenlabs_client = ElevenLabs(
            api_key=os.getenv("ELEVENLABS_API_KEY")
        )

    def generate_voiceover(self, text, output_file="voiceover.mp3"):
        audio = self.elevenlabs_client.generate(text=text, voice="Aria", model="eleven_monolingual_v1")
        output_filepath = os.path.join('data/voice', output_file)
        elevenlabs.save(audio, output_filepath)
        return audio
