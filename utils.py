import os
import shutil
import yt_dlp
import ffmpeg
import srt
from moviepy.editor import VideoFileClip
import whisper
from fpdf import FPDF
from datetime import timedelta

def extract_audio(video_path, audio_path):
    try:
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path)
    except Exception as e:
        print(f"Error extracting audio: {e}")
        raise

def transcribe_audio(audio_path, model_size="base"):
    try:
        model = whisper.load_model(model_size)
        # Enable word-level timestamps
        result = model.transcribe(audio_path, word_timestamps=True)
        return result['segments']
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        raise

def create_srt(segments, srt_path, max_chars=42, max_duration=3):
    subtitles = []
    index = 1
    for segment in segments:
        words = segment.get('words', [])
        if not words:
            words = [{'word': w, 'start': segment['start'], 'end': segment['end']} for w in segment['text'].split()]
        current_sub = ""
        phrase_start = None

        for word_info in words:
            word = word_info['word'].strip()
            word_start = word_info['start']
            word_end = word_info['end']
            if not phrase_start:
                phrase_start = timedelta(seconds=word_start)
                start_time = phrase_start
            end_time = timedelta(seconds=word_end)
            duration = (end_time - phrase_start).total_seconds()

            if len(current_sub) + len(word) + 1 > max_chars or duration > max_duration:
                subtitles.append(srt.Subtitle(index=index, start=start_time, end=end_time, content=current_sub.strip()))
                index += 1
                current_sub = word + " "
                phrase_start = timedelta(seconds=word_start)
                start_time = phrase_start
            else:
                current_sub += word + " "

        if current_sub:
            subtitles.append(srt.Subtitle(index=index, start=phrase_start, end=end_time, content=current_sub.strip()))
            index += 1

    srt_content = srt.compose(subtitles)
    try:
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
    except Exception as e:
        print(f"Error writing SRT file: {e}")
        raise

def create_pdf(segments, pdf_path):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)

        for segment in segments:
            start_time = str(timedelta(seconds=segment['start'])).split('.')[0]
            end_time = str(timedelta(seconds=segment['end'])).split('.')[0]
            text = segment['text'].strip()

            pdf.multi_cell(0, 10, f"[{start_time} - {end_time}]")
            pdf.multi_cell(0, 10, text)
            pdf.ln(1)

        pdf.output(pdf_path)
        print(f"PDF transcript created at: {pdf_path}")
    except Exception as e:
        print(f"Error creating PDF: {e}")
        raise

def embed_subtitles_hardcode(video_path, srt_path, output_path):
    try:
        subtitle_style = (
            "FontSize=16,PrimaryColour=&HFFFFFF&,BackColour=&H80000000&,"
            "BorderStyle=1,Outline=1,OutlineColour=&H000000&,Shadow=1,ShadowColour=&H000000&,"
            "Alignment=2,MarginV=10"
        )
        ffmpeg_filter = f"subtitles={srt_path}:force_style='{subtitle_style}'"
        ffmpeg.input(video_path).output(output_path, vf=ffmpeg_filter).run(overwrite_output=True)
    except ffmpeg.Error as e:
        print(f"FFmpeg error: {e}")
        raise

def fetch_video_info(video_url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(video_url, download=False)
            print(f"Info dict: {info_dict}")  # Debugging output
            formats = info_dict.get('formats', [])
            # Extract available qualities
            valid_qualities = {'144p', '240p', '360p', '480p', '720p', '1080p'}
            qualities = {}
            for fmt in formats:
                height = fmt.get('height')
                if height:
                    quality = f"{height}p"
                    if quality in valid_qualities and quality not in qualities:
                        qualities[quality] = None
            # Sort qualities
            sorted_qualities = sorted(qualities.keys(), key=lambda x: int(x.rstrip('p')), reverse=True)
            return sorted_qualities
        except Exception as e:
            return f"Error fetching video info: {str(e)}"



def download_youtube_video(video_url, selected_quality, download_dir="temp_video"):
    quality_number = selected_quality.split('p')[0]
    ydl_opts = {
        'format': f'bestvideo[height<={quality_number}]+bestaudio/best[height<={quality_number}]',
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(video_url, download=True)
            video_path = ydl.prepare_filename(info_dict)
            # Handle cases where the downloaded filename might have different extensions
            if not os.path.exists(video_path):
                possible_exts = ['mp4', 'webm', 'mkv']
                base_path = os.path.splitext(video_path)[0]
                for ext in possible_exts:
                    trial_path = f"{base_path}.{ext}"
                    if os.path.exists(trial_path):
                        video_path = trial_path
                        break
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Downloaded video file not found: {video_path}")
            return video_path
        except Exception as e:
            raise Exception(f"Error downloading video: {str(e)}")

def process_video(video_path, model_size="base"):
    audio_path = "temp_audio.wav"
    srt_path = "temp_subtitles.srt"
    output_video_path = os.path.join("output", f"output_{os.path.basename(video_path)}")
    output_pdf_path = os.path.join("output", f"transcript_{os.path.basename(video_path)}.pdf")

    try:
        extract_audio(video_path, audio_path)
        segments = transcribe_audio(audio_path, model_size=model_size)
        create_srt(segments, srt_path)
        embed_subtitles_hardcode(video_path, srt_path, output_video_path)
        create_pdf(segments, output_pdf_path)
        print("Video and PDF processing completed successfully.")
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
        if os.path.exists(srt_path):
            os.remove(srt_path)
        if os.path.exists(video_path):
            os.remove(video_path)  # Remove the downloaded video to save space

def handle_upload_video(video_file):
    if not video_file:
        return None, None, "Please upload a video file."
    try:
        video_path = video_file  # Use the file path string directly

        # Define the destination directory as an absolute path
        temp_video_dir = os.path.abspath("temp_video")

        # Ensure the temp_video directory exists
        os.makedirs(temp_video_dir, exist_ok=True)

        # Construct the new path
        new_path = os.path.join(temp_video_dir, os.path.basename(video_path))

        # Move the uploaded video to temp_video directory using shutil.move
        if not os.path.abspath(video_path).startswith(temp_video_dir):
            shutil.move(video_path, new_path)
            video_path = new_path

        process_video(video_path)
        output_video_path = os.path.join("output", f"output_{os.path.basename(video_path)}")
        output_pdf_path = os.path.join("output", f"transcript_{os.path.basename(video_path)}.pdf")
        return output_video_path, output_pdf_path, ""
    except Exception as e:
        return None, None, f"Error processing uploaded video: {str(e)}"

def handle_fetch_info(video_url):
    if not video_url:
        return [], "Please enter a YouTube URL."
    quality_options = fetch_video_info(video_url)
    if isinstance(quality_options, str) and quality_options.startswith("Error"):
        return [], quality_options
    return quality_options, ""

def handle_process_video(video_url, selected_quality):
    if not video_url:
        return None, None, "Please enter a YouTube URL."
    try:
        video_path = download_youtube_video(video_url, selected_quality)
    except Exception as e:
        return None, None, str(e)
    
    try:
        process_video(video_path)
        output_video_path = os.path.join("output", f"output_{os.path.basename(video_path)}")
        output_pdf_path = os.path.join("output", f"transcript_{os.path.basename(video_path)}.pdf")
        return output_video_path, output_pdf_path, ""
    except Exception as e:
        return None, None, f"Error processing video: {str(e)}"
