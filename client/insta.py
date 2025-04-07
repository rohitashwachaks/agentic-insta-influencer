import ast
import json
import os
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from tqdm import tqdm
import logging

from common.utils import crop_audio_ffmpeg, to_snake_case

insta_logger = logging.getLogger()


class InstagramClient:
    def __init__(self):
        self.client = Client()

    def login(self):
        """
            Attempts to login to Instagram using either the provided session information
            or the provided username and password.
        """
        USERNAME = os.getenv("IG_USERNAME")
        PASSWORD = os.getenv("IG_PASSWORD")

        self.client = Client()
        try:
            session = self.client.load_settings("session.json")
        except FileNotFoundError:
            session = None

        login_via_session = False
        login_via_pw = False

        if session:
            try:
                self.client.set_settings(session)
                self.client.login(USERNAME, PASSWORD)

                # check if session is valid
                try:
                    self.client.get_timeline_feed()
                except LoginRequired:
                    insta_logger.info("Session is invalid, need to login via username and password")

                    old_session = self.client.get_settings()

                    # use the same device uuids across logins
                    self.client.set_settings({})
                    self.client.set_uuids(old_session["uuids"])

                    self.client.login(USERNAME, PASSWORD)
                login_via_session = True
            except Exception as e:
                insta_logger.info("Couldn't login user using session information: %s" % e)

        if not login_via_session:
            try:
                insta_logger.info("Attempting to login via username and password. username: %s" % USERNAME)
                if self.client.login(USERNAME, PASSWORD):
                    self.client.dump_settings("session.json")
                    login_via_pw = True
            except Exception as e:
                insta_logger.info("Couldn't login user using username and password: %s" % e)

        if not login_via_pw and not login_via_session:
            raise Exception("Couldn't login user with either password or session")

    def post_to_instagram(self, image_path, caption):
        self.client.photo_upload(image_path, caption)
        print("Post uploaded successfully!")

    def post_reel_to_instagram(self, video_path, caption):
        self.client.video_upload(video_path, caption)
        print("Reel uploaded successfully!")

    def fetch_trending_audio(self, keyword: str, verbose: bool = False, force_download: bool = False):
        """
        Fetch trending audio on Instagram.
        :param force_download:
        :param verbose:
        :param keyword:
        :return:
        """
        DATA_DIR = os.path.join(os.getenv('DATA_DIR'), keyword)
        REEL_AUDIO_DIR = os.path.join(DATA_DIR, 'audio')

        # Check if folder exists
        if os.path.exists(REEL_AUDIO_DIR) and not force_download:
            print(f"Folder already exists: {REEL_AUDIO_DIR}")
            # Check if there are any audio files in the folder and return the names if there are.
            # Else, run the download process.
            audio_files = [f for f in os.listdir(REEL_AUDIO_DIR) if
                           f.endswith('.mp3') or f.endswith('.m4a') or f.endswith('.wav') or f.endswith('.mp4')]
            audio_meta = json.load(open(os.path.join(DATA_DIR, 'audio_meta.json'), 'r'))
            if len(audio_files) > 0:
                print(f"Audio files already exist in folder: {DATA_DIR}")
                return audio_files, audio_meta
            else:
                print("Folder exists but no audio files found")

        # Create folder if it doesn't exist

        print(f"Downloading new audio files to: {DATA_DIR}")
        os.makedirs(REEL_AUDIO_DIR, exist_ok=True)

        # Remove all files in the folder
        for f in os.listdir(REEL_AUDIO_DIR):
            os.remove(os.path.join(REEL_AUDIO_DIR, f))

        # search for trending audios
        trending_audios = self.client.search_music(keyword)

        if len(trending_audios) == 0:
            print(f"No trending audio found for keyword: {keyword}")
            with open(os.path.join(DATA_DIR, 'audio_meta.json'), 'w') as f:
                json.dump({}, f, indent=2)
            return [], []

        pbar = tqdm(trending_audios) if verbose else trending_audios

        files_downloaded = []
        audio_meta = {}
        for reel_audio in pbar:
            if verbose:
                pbar.set_description(f"Downloading {reel_audio.title}")
            track_uri = reel_audio.uri
            extension = os.path.splitext(track_uri.path)[1]
            filename = to_snake_case(reel_audio.title)
            self.client.track_download_by_url(track_uri, folder=REEL_AUDIO_DIR, filename=filename)

            # convert reel_audio object to dict and save the file as a json
            files_downloaded.append(f'{filename}{extension}')
            audio_meta[f'{filename}{extension}'] = json.loads(reel_audio.model_dump_json())

        with open(os.path.join(DATA_DIR, 'audio_meta.json'), 'w') as f:
            json.dump(audio_meta, f, indent=2)
        return files_downloaded, audio_meta



            # crop_audio_ffmpeg(
            #     input_file=os.path.join(REEL_AUDIO_DIR, f'{filename}{extension}'),
            #     start_time=reel_audio.highlight_start_times_in_ms[0],
            #     duration=30000,  # 30 seconds
            #     output_folder=REEL_AUDIO_DIR,
            #     # output_file=os.path.join(REEL_AUDIO_DIR, f'{filename}.mp3')
            # )