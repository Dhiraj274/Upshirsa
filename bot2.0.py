import os
import logging
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)
from utils import (
    process_video,
    fetch_video_info,
    download_youtube_video,
)
import asyncio

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Set to DEBUG for detailed logs
)
logger = logging.getLogger(__name__)

# Define conversation states
CHOOSING, PROCESS_VIDEO, PROCESS_YOUTUBE = range(3)

# Replace with your actual bot token (ensure it's secure)
BOT_TOKEN = '7566466111:AAETQgIP6hS3FCY_or9AYAP8fA_sj7Pr5T8'  # Replace with the new token

# Ensure necessary directories exist
os.makedirs("temp_video", exist_ok=True)
os.makedirs("output", exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sends a welcome message with options to the user."""
    welcome_message = (
        "👋 *Welcome to Upshirsa Subtitle Generator Bot!*\n\n"
        "Please choose an option below to proceed:"
    )
    
    # Define inline buttons
    keyboard = [
        [
            InlineKeyboardButton("📹 Send Video", callback_data='send_video'),
            InlineKeyboardButton("🔗 Send YouTube Link", callback_data='send_youtube')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_markdown(welcome_message, reply_markup=reply_markup)
    
    return CHOOSING

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a help message to the user."""
    help_message = (
        "🛠 *Upshirsa Subtitle Generator Bot Help*\n\n"
        "*Commands:*\n"
        "/start - Show welcome message and options\n"
        "/help - Show this help message\n\n"
        "*How to use:*\n"
        "• Click on 'Send Video' to upload a video file.\n"
        "• Click on 'Send YouTube Link' to provide a YouTube URL.\n"
    )
    await update.message.reply_markdown(help_message)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles button clicks and sets the conversation state."""
    query = update.callback_query
    await query.answer()
    
    choice = query.data
    
    if choice == 'send_video':
        await query.edit_message_text(text="📹 *Please upload the video file you want to process:*", parse_mode='Markdown')
        return PROCESS_VIDEO
    elif choice == 'send_youtube':
        await query.edit_message_text(text="🔗 *Please send the YouTube video URL you want to process:*", parse_mode='Markdown')
        return PROCESS_YOUTUBE
    else:
        await query.edit_message_text(text="❌ *Invalid selection. Please try again.*", parse_mode='Markdown')
        return CHOOSING

async def send_files(update: Update, context: ContextTypes.DEFAULT_TYPE, video_path, pdf_path):
    """Sends the processed video and PDF transcript to the user."""
    # Verify files exist
    if not os.path.exists(video_path):
        logger.error(f"Processed video file does not exist: {video_path}")
        await update.message.reply_text("❌ Processed video file not found.")
        return

    if not os.path.exists(pdf_path):
        logger.error(f"PDF transcript file does not exist: {pdf_path}")
        await update.message.reply_text("❌ PDF transcript file not found.")
        return

    # Get file sizes
    video_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
    pdf_size = os.path.getsize(pdf_path) / (1024 * 1024)      # MB
    logger.info(f"Sending video: {video_path} ({video_size:.2f} MB)")
    logger.info(f"Sending PDF: {pdf_path} ({pdf_size:.2f} MB)")

    # Check PDF size against Telegram's limit (50 MB for regular users)
    if pdf_size > 50:
        await update.message.reply_text("❌ The generated PDF is too large to send (over 50 MB). Please try processing a shorter video.")
        logger.error(f"PDF size exceeds limit: {pdf_size:.2f} MB")
        return

    # Send Video
    try:
        with open(video_path, 'rb') as video_file:
            await update.message.reply_video(
                video=InputFile(video_file),
                caption="🎥 *Here is your video with embedded subtitles!*",
                parse_mode='Markdown'
            )
        logger.info(f"Successfully sent video: {video_path}")
    except Exception as e:
        logger.error(f"Error sending video: {e}")
        await update.message.reply_text(f"❌ An error occurred while sending the video: {e}")

    # Send PDF
    try:
        with open(pdf_path, 'rb') as pdf_file:
            await update.message.reply_document(
                document=InputFile(pdf_file),
                filename=os.path.basename(pdf_path),
                caption="📄 *Here is the PDF transcript!*"
            )
        logger.info(f"Successfully sent PDF: {pdf_path}")
    except Exception as e:
        logger.error(f"Error sending PDF: {e}")
        await update.message.reply_text(f"❌ An error occurred while sending the PDF transcript: {e}")

async def handle_video_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes the uploaded video."""
    video = update.message.video or update.message.document
    if not video:
        await update.message.reply_text("❌ Please upload a valid video file.")
        return CHOOSING

    # Check file size
    file_size = video.file_size / (1024 * 1024)  # Size in MB
    if file_size > 100:  # Adjust as needed
        await update.message.reply_text("❌ The video is too large. Please upload a video smaller than 100 MB.")
        return CHOOSING

    # Acknowledge the upload
    await update.message.reply_text("✅ Video received! Processing... Please wait.")

    try:
        # Download the video
        file_id = video.file_id
        new_file = await context.bot.get_file(file_id)
        # Sanitize filename to prevent issues
        video_filename = f"{file_id}_{os.path.basename(video.file_name)}"
        video_path = os.path.join("temp_video", video_filename)
        await new_file.download_to_drive(video_path)
        logger.info(f"Downloaded video to: {video_path}")

        # Process the video using utils.py in a separate thread
        await update.message.reply_text("🔄 Processing the video. This might take a few moments...")
        processed_video_path, output_pdf_path = await asyncio.to_thread(process_video, video_path)
        logger.info(f"Processed video at: {processed_video_path}")
        logger.info(f"Generated PDF at: {output_pdf_path}")

        # Send the files
        await send_files(update, context, processed_video_path, output_pdf_path)

    except Exception as e:
        logger.error(f"Error processing video: {e}")
        await update.message.reply_text(f"❌ An error occurred while processing the video: {e}")

    finally:
        # Clean up temporary files
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                logger.debug(f"Removed temporary video file: {video_path}")
            if 'processed_video_path' in locals() and os.path.exists(processed_video_path):
                os.remove(processed_video_path)
                logger.debug(f"Removed processed video file: {processed_video_path}")
            if 'output_pdf_path' in locals() and os.path.exists(output_pdf_path):
                os.remove(output_pdf_path)
                logger.debug(f"Removed PDF transcript file: {output_pdf_path}")
        except Exception as cleanup_error:
            logger.error(f"Error cleaning up files: {cleanup_error}")

    # Return to the main menu
    await start(update, context)
    return CHOOSING

async def handle_youtube_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes the provided YouTube URL."""
    text = update.message.text.strip()
    if not text.startswith(("http://", "https://")):
        await update.message.reply_text("❌ Please send a valid YouTube URL.")
        return CHOOSING

    youtube_url = text
    await update.message.reply_text("✅ YouTube link received! Fetching video information...")

    try:
        # Fetch available qualities
        qualities = fetch_video_info(youtube_url)
        if isinstance(qualities, str):
            # An error occurred
            await update.message.reply_text(f"❌ {qualities}")
            return CHOOSING

        if not qualities:
            await update.message.reply_text("❌ No valid video qualities found.")
            return CHOOSING

        # Select the highest available quality
        selected_quality = qualities[0]  # Assuming qualities are sorted from highest to lowest
        await update.message.reply_text(f"🔍 Selected quality: {selected_quality}\n🔄 Processing video... Please wait.")

        # Download the YouTube video
        video_path = download_youtube_video(youtube_url, selected_quality)
        logger.info(f"Downloaded YouTube video to: {video_path}")

        # Process the video
        processed_video_path, output_pdf_path = await asyncio.to_thread(process_video, video_path)
        logger.info(f"Processed video at: {processed_video_path}")
        logger.info(f"Generated PDF at: {output_pdf_path}")

        # Send the files
        await send_files(update, context, processed_video_path, output_pdf_path)

    except Exception as e:
        logger.error(f"Error processing YouTube video: {e}")
        await update.message.reply_text(f"❌ An error occurred while processing the YouTube video: {e}")

    finally:
        # Clean up temporary files
        try:
            if 'video_path' in locals() and os.path.exists(video_path):
                os.remove(video_path)
                logger.debug(f"Removed temporary YouTube video file: {video_path}")
            if 'processed_video_path' in locals() and os.path.exists(processed_video_path):
                os.remove(processed_video_path)
                logger.debug(f"Removed processed video file: {processed_video_path}")
            if 'output_pdf_path' in locals() and os.path.exists(output_pdf_path):
                os.remove(output_pdf_path)
                logger.debug(f"Removed PDF transcript file: {output_pdf_path}")
        except Exception as cleanup_error:
            logger.error(f"Error cleaning up files: {cleanup_error}")

    # Return to the main menu
    await start(update, context)
    return CHOOSING

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text(
        "Operation cancelled. To start again, type /start.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📌 Main Menu", callback_data='main_menu')]
        ])
    )
    return ConversationHandler.END

async def main_menu_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sends the main menu options."""
    await start(update, context)
    return CHOOSING

def main():
    """Starts the bot."""
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .read_timeout(30)    # Set read timeout to 30 seconds
        .write_timeout(30)   # Set write timeout to 30 seconds
        .build()
    )

    # Define the ConversationHandler with the states CHOOSING, PROCESS_VIDEO, PROCESS_YOUTUBE
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                CallbackQueryHandler(button, pattern='^(send_video|send_youtube)$'),
                CallbackQueryHandler(main_menu_button, pattern='^main_menu$')
            ],
            PROCESS_VIDEO: [
                MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video_upload),
                CommandHandler('cancel', cancel)
            ],
            PROCESS_YOUTUBE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_youtube_url),
                CommandHandler('cancel', cancel)
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CallbackQueryHandler(main_menu_button, pattern='^main_menu$')
        ],
    )

    # Register handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))

    # Start the Bot
    logger.info("Starting Upshirsa Subtitle Generator Bot...")
    application.run_polling()

if __name__ == '__main__':
    main()
