import os

import ffmpeg

import re


def to_snake_case(s):
    """Converts a string to snake_case format."""
    s = re.sub(r'[^a-zA-Z0-9]+', '_', s)  # Replace non-alphanumeric characters with underscores
    s = re.sub(r'(_)+', '_', s)  # Remove duplicate underscores
    return s.strip('_').lower()  # Strip leading/trailing underscores and convert to lowercase


def crop_audio_ffmpeg(input_file: str, start_time: int, duration: int, output_file: str):
    try:
        end_time = start_time + duration
        (
            ffmpeg
            # .input(input_file, ss=start_time, to=end_time)
            .input(input_file, ss=start_time, t=duration)
            .output(output_file, format="mp3", acodec="libmp3lame")
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )
        print(f"Cropped audio saved as {output_file}")
        return output_file
    except ffmpeg.Error as e:
        print("FFmpeg error:", output_file)  # Print detailed error message
        return None