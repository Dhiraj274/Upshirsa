import os
import gradio as gr
from utils import (
    fetch_video_info,
    download_youtube_video,
    process_video
)
import shutil

# Ensure output directories exist
os.makedirs("output", exist_ok=True)
os.makedirs("temp_video", exist_ok=True)

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

def fetch_video_info_ui(video_url):
    if not video_url:
        return gr.update(choices=[], value=None), "Please enter a YouTube URL."
    
    quality_options = fetch_video_info(video_url)
    
    if isinstance(quality_options, str) and quality_options.startswith("Error"):
        return gr.update(choices=[], value=None), quality_options
    
    # Debugging: Log the quality options retrieved
    print(f"Quality options retrieved: {quality_options}")

    return gr.update(choices=quality_options, value=quality_options[0] if quality_options else None), ""




def handle_process_video_ui(video_url, selected_quality="720p"):  # Default to 720p
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


# Gradio UI with Tabs
def launch_ui():
    with gr.Blocks() as app:
        # Centered title with custom styling
        gr.Markdown(
            """
            <div style="text-align: center;">
                <h1 style="font-size: 3em;">Upshirsa 🎥📝</h1>
                <h4 style="font-size: 1.5em;">Subtitle generator</h4>
            </div>
            """, 
            elem_id="title"
        )
        
        with gr.Tab("Upload Video"):
            gr.Markdown("## Upload Your Video File")
            
            with gr.Row():
                upload_video = gr.Video(label="Upload Video File")
            
            process_upload_button = gr.Button("Process Uploaded Video 🎬")
            
            with gr.Row():
                upload_output_video = gr.File(label="Download the Captioned Video 📥")
                upload_output_pdf = gr.File(label="Download the Transcript PDF 📄")
            
            # Upload video processing
            process_upload_button.click(
                handle_upload_video,
                inputs=[upload_video],
                outputs=[upload_output_video, upload_output_pdf]
            )
        
        with gr.Tab("YouTube Link"):
            gr.Markdown("## Process a YouTube Video")
            
            with gr.Row():
                youtube_url = gr.Textbox(label="Enter YouTube Video URL", placeholder="https://www.youtube.com/watch?v=example")
            
            process_youtube_button = gr.Button("Process YouTube Video 🎬")
            
            with gr.Row():
                youtube_output_video = gr.File(label="Download the Captioned Video 📥")
                youtube_output_pdf = gr.File(label="Download the Transcript PDF 📄")
            
            # Process YouTube video
            process_youtube_button.click(
                lambda url: handle_process_video_ui(url, "720p"),  # Use the default quality directly
                inputs=[youtube_url],
                outputs=[youtube_output_video, youtube_output_pdf]
            )

    app.launch(share=True)


if __name__ == "__main__":
    launch_ui()
