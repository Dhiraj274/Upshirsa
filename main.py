import os
import argparse
from utils import extract_audio, transcribe_audio, create_srt, embed_subtitles_hardcode, create_pdf, fetch_video_info, download_youtube_video, process_video

def process_youtube_video(video_url, selected_quality, model_size="base"):
    try:
        video_path = download_youtube_video(video_url, selected_quality)
        process_video(video_path, model_size=model_size)
    except Exception as e:
        print(f"Error processing YouTube video: {e}")

def main():
    parser = argparse.ArgumentParser(description="Video Transcriber CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subparser for processing a local video file
    parser_local = subparsers.add_parser('local', help="Process a local video file")
    parser_local.add_argument('video_path', type=str, help="Path to the local video file")
    parser_local.add_argument('--model', type=str, default="base", help="Whisper model size")

    # Subparser for processing a YouTube video
    parser_youtube = subparsers.add_parser('youtube', help="Process a YouTube video")
    parser_youtube.add_argument('video_url', type=str, help="URL of the YouTube video")
    parser_youtube.add_argument('--quality', type=str, required=True, help="Desired video quality (e.g., 720p)")
    parser_youtube.add_argument('--model', type=str, default="base", help="Whisper model size")

    args = parser.parse_args()

    os.makedirs("output", exist_ok=True)
    os.makedirs("temp_video", exist_ok=True)

    if args.command == 'local':
        process_video(args.video_path, model_size=args.model)
    elif args.command == 'youtube':
        process_youtube_video(args.video_url, args.quality, model_size=args.model)

if __name__ == "__main__":
    main()
