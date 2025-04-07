from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip


def create_reel(video_path, audio_path, text, output_path="reel.mp4"):
    video = VideoFileClip(video_path).subclip(0, 10)  # Use first 10 sec
    audio = AudioFileClip(audio_path)

    # Add text overlay
    txt_clip = TextClip(text, fontsize=40, color='white', font='Arial-Bold')
    txt_clip = txt_clip.set_position('bottom').set_duration(video.duration)

    final_clip = CompositeVideoClip([video, txt_clip]).set_audio(audio)
    final_clip.write_videofile(output_path, codec="libx264", fps=24)

    return output_path
