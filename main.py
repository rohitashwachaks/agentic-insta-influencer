import os
import random
from pathlib import Path
from typing import List

from dotenv import load_dotenv

from client.insta import InstagramClient
from client.openai import OpenAIClient
from client.reel_creator import ReelCreatorClient
from image_vector_store.vectorstore import VectorStore

if __name__ == '__main__':
    load_dotenv()  # Load API key from .env file

    # vibe = 'badass adventure'
    # destination = 'Lower Antelope Canyons, Arizona'
    # duration = 10

    vs = VectorStore()
    image_dir = Path("./data/x")
    images = [str(p) for p in image_dir.glob("*.jpeg")]

    vs.upsert_batch(images)

    # # Login to Instagram
    # insta_client = InstagramClient()
    # insta_client.login()

    # # Fetch trending audios
    # trending_audios, audio_meta = insta_client.fetch_trending_audio(vibe, verbose=True)  #, force_download=True)
    # print(trending_audios)
    #
    # # Convert mp4 to mp3 and crop audio
    # reel_creator = ReelCreatorClient(vibe)
    # cropped_audio_files: List[str] = reel_creator.crop_audio(duration)

    # # Detect beats in audio
    # # Select a random audio file from the cropped audio files
    # cropped_audio_files = [os.path.join(f'./data/{vibe}/output', f) for f in os.listdir(f'./data/{vibe}/output') if f.endswith(f'-{duration}s.mp3')]
    # audio_file = random.choice(cropped_audio_files)
    # print("Selected audio file:", audio_file)
    # beat_times = reel_creator.detect_beats(audio_file)
    # print("Beat drop timestamps:", beat_times)
    #
    # # Create reel
    # output_reel = f"./data/{vibe}/content/final_reel.mp4"
    # reel_creator.create_reel(
    #     image_paths=[os.path.join(f'./data/{vibe}/content', f) for f in os.listdir(f'./data/{vibe}/content') if f.endswith('.jpeg')],
    #     video_paths=[os.path.join(f'./data/{vibe}/content', f) for f in os.listdir(f'./data/{vibe}/content') if f.endswith('.mp4')],
    #     audio_path=audio_file,
    #     beat_times=beat_times,
    #     output_file=output_reel
    # )
    #
    # openai_client = OpenAIClient()
    #
    # caption = openai_client.generate_caption(destination, vibe)
    # print('Caption:', caption)
    #
    # # Upload reel to Instagram
    # insta_client.post_reel_to_instagram(output_reel, caption)
    #
    # # Generate voice using ElevenLabs
    # # from client.elevenlabs import ElevenLabsClient
    # # elevenlabs_client = ElevenLabsClient()
    # #
    # # voice = elevenlabs_client.generate_voiceover(caption, f'{destination}.mp3')
    #
    # # # Post to Instagram
    # # image_path = 'data/images/pigeon_forge.jpeg'
    # # insta_client.post_to_instagram(image_path, caption)
