
# Upshirsa 🎥📝

## Subtitle and Transcript Generator

Upshirsa is a video processing tool designed to extract subtitles and transcripts from videos. The application allows users to upload local videos or input YouTube video URLs, and it automatically generates captioned videos with hardcoded subtitles and provides transcripts in PDF format. It supports various video qualities and uses the Whisper ASR model to transcribe audio into text.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Web Interface](#web-interface)
  - [Command Line Interface (CLI)](#command-line-interface-cli)
- [Dependencies](#dependencies)
- [Configuration](#configuration)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Contributors](#contributors)
- [License](#license)

---

## Features

- Upload and process local videos.
- Process YouTube videos and download with selectable quality.
- Generate transcripts in PDF format.
- Generate subtitles in `.srt` format.
- Automatically embed subtitles (hardcoded) into the video.
- Multi-platform support using [Gradio](https://gradio.app) for web-based UI and command-line interface for advanced users.

---

## Installation

### Prerequisites

- Python 3.7+
- FFmpeg installed and accessible via the command line.
- Install the required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

### FFmpeg Installation
To ensure video processing, make sure FFmpeg is installed on your system. You can install it via:
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`
- **Windows**: Download from [FFmpeg official website](https://ffmpeg.org/download.html).

---

## Usage

### Web Interface

You can run the Gradio-based web UI by executing the following command:

```bash
python ui.py
```

This will launch a web interface with two options:
1. **Upload Video**: Upload a local video to generate subtitles and transcripts.
2. **YouTube Link**: Enter a YouTube URL to download, transcribe, and caption the video.

After processing, you can download both the captioned video and the transcript in PDF format.

### Command Line Interface (CLI)

For advanced users, a CLI is available. You can process both local and YouTube videos.

#### Processing a Local Video

```bash
python main.py local <path_to_video> --model base
```

For example:

```bash
python main.py local sample.mp4 --model small
```

#### Processing a YouTube Video

```bash
python main.py youtube <video_url> --quality 720p --model base
```

For example:

```bash
python main.py youtube https://www.youtube.com/watch?v=example --quality 720p --model small
```

---

## Dependencies

The project relies on the following dependencies:

- [gradio](https://gradio.app) - Web UI framework for Python.
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube video downloader.
- [moviepy](https://github.com/Zulko/moviepy) - Video editing library for Python.
- [whisper](https://github.com/openai/whisper) - Whisper ASR model for transcriptions.
- [ffmpeg-python](https://github.com/kkroening/ffmpeg-python) - FFmpeg bindings for Python.
- [srt](https://github.com/cdown/srt) - Python library for `.srt` subtitle file creation.
- [fpdf](https://pyfpdf.github.io/fpdf2) - PDF generation library for Python.

Install them using the following command:

```bash
pip install -r requirements.txt
```

---

## Configuration

You can customize the transcription model size (`base`, `small`, `medium`, `large`) and video quality by passing arguments in the CLI or modifying defaults in the UI.

- **Model size**: Select the Whisper model size for transcription accuracy and speed. Example: `--model large`.
- **Video quality**: For YouTube videos, you can specify the quality (e.g., `720p`, `1080p`) by using `--quality`.

---

## Examples

1. **Upload Video**:
   - Upload a video through the web UI to get hardcoded subtitles and a transcript.
   
2. **YouTube Video**:
   - Provide a YouTube URL and select video quality (e.g., 720p).
   - Download the captioned video and transcript.

3. **CLI Example**:
   - For local videos: `python main.py local sample.mp4 --model base`
   - For YouTube videos: `python main.py youtube https://youtube.com/watch?v=example --quality 720p`

---

## Troubleshooting

- **FFmpeg Errors**: Ensure FFmpeg is installed and added to your system's PATH.
- **Whisper Model Load Failures**: Ensure the Whisper model is downloaded properly and matches the specified size (e.g., `base`, `small`).
- **Incorrect SRT Generation**: If the subtitles are out of sync, ensure the correct video frame rate is maintained during processing.

---

## Contributors

- **Dhiraj Vaghela** - Developer

Feel free to contribute to this project by submitting issues or pull requests.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
