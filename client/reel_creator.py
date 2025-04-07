import itertools
import json
import os
from typing import Optional

import librosa
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, ImageSequenceClip

from common.utils import crop_audio_ffmpeg

DURATION = [5, 10, 15, 30]


class ReelCreatorClient:
    def __init__(self, keyword):
        self.DATA_DIR = os.path.join(os.getenv('DATA_DIR'), keyword)
        self.REEL_AUDIO_DIR = os.path.join(self.DATA_DIR, 'audio')
        self.REEL_CONTENT_DIR = os.path.join(self.DATA_DIR, 'content')
        # self.REEL_VIDEO_DIR = os.path.join(self.DATA_DIR, 'video')
        # self.REEL_IMAGE_DIR = os.path.join(self.DATA_DIR, 'images')
        self.REEL_OUTPUT_DIR = os.path.join(self.DATA_DIR, 'output')
        # self.REEL_CAPTION_DIR = os.path.join(self.DATA_DIR, 'captions')
        self.REEL_VOICEOVER_DIR = os.path.join(self.DATA_DIR, 'voice')

    def crop_audio(self, duration: Optional[int] = None):
        duration_list = DURATION if duration is None else [duration]
        audio_meta_dict = json.load(open(os.path.join(self.DATA_DIR, 'audio_meta.json')))

        os.makedirs(self.REEL_OUTPUT_DIR, exist_ok=True)
        # Remove all files in the folder
        for f in os.listdir(self.REEL_OUTPUT_DIR):
            os.remove(os.path.join(self.REEL_OUTPUT_DIR, f))

        cropped_audio_files_list = []

        for filename_extension, meta in audio_meta_dict.items():
            filename, _ = filename_extension.rsplit('.')

            for start_time, duration in itertools.product(meta['highlight_start_times_in_ms'][:1], duration_list):
                start_time = start_time / 1000
                cropped_audio_file = f"{filename}-{int(start_time)}-{duration}s.mp3"

                input_file = os.path.join(self.REEL_AUDIO_DIR, filename_extension)
                output_file = os.path.join(self.REEL_OUTPUT_DIR, cropped_audio_file)
                crop_audio_ffmpeg(
                    input_file=input_file,
                    start_time=start_time, duration=duration,
                    output_file=output_file
                )
                cropped_audio_files_list.append(output_file)
        return cropped_audio_files_list

    def detect_beats(self, audio_path):
        y, sr = librosa.load(audio_path, sr=None)
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beats, sr=sr)
        return beat_times

    def create_reel(self, image_paths, video_paths, audio_path, beat_times, output_file="final_reel.mp4"):
        clips = []
        for i, image in enumerate(image_paths):
            if i >= len(beat_times):
                break
            duration = beat_times[i + 1] - beat_times[i] if i + 1 < len(beat_times) else 1
            img_clip = ImageSequenceClip([image], durations=[duration])
            clips.append(img_clip)

        # for i, video in enumerate(video_paths):
        #     duration = beat_times[i + 1] - beat_times[i] if i + 1 < len(beat_times) else 1
        #     vid_clip = VideoFileClip(video).subclip(0, duration)
        #     clips.append(vid_clip)

        final_video = concatenate_videoclips(clips, method="compose")
        audio = AudioFileClip(audio_path)
        final_video = final_video.set_audio(audio)

        final_video.write_videofile(output_file, codec="libx264", fps=24)
        return output_file

    # Example usage
    # image_paths = ["img1.jpg", "img2.jpg"]
    # video_paths = ["clip1.mp4", "clip2.mp4"]
    # final_reel = create_reel(image_paths, video_paths, audio_file, beat_times)
