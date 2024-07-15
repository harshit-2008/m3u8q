import os
import subprocess
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Define your bot token here
TOKEN = '7439562089:AAHO4EVt3g_R9-9gjqX3J7_lLTusprisdgE'

# Directory where recordings will be saved
DOWNLOAD_DIR = 'downloads'

# Create the download directory if it does not exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Hello! Send me a live M3U8 URL and I'll record the stream for you. Use /help for more details."
    )

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Send me a live M3U8 URL to start recording. I will send you the recorded video once done."
    )

def record_m3u8(update: Update, context: CallbackContext) -> None:
    m3u8_url = update.message.text

    if not m3u8_url.startswith('http://') and not m3u8_url.startswith('https://'):
        update.message.reply_text('Please send a valid M3U8 URL.')
        return

    file_name = m3u8_url.split('/')[-1].replace('.m3u8', '.mp4')
    file_path = os.path.join(DOWNLOAD_DIR, file_name)

    # Start recording using ffmpeg
    command = [
        'ffmpeg',
        '-i', m3u8_url,
        '-c', 'copy',
        '-f', 'mp4',
        '-t', '00:10:00',  # Record for 10 minutes, adjust as needed
        file_path
    ]

    update.message.reply_text('Recording started, this may take a while depending on the stream length.')

    try:
        subprocess.run(command, check=True)
        update.message.reply_text('Recording finished. Sending you the video now.')

        # Send the recorded video to the user
        with open(file_path, 'rb') as video_file:
            update.message.reply_video(video_file)

        # Remove the file after sending
        os.remove(file_path)
    except subprocess.CalledProcessError:
        update.message.reply_text('Failed to record the stream. Please try again later.')
    except Exception as e:
        update.message.reply_text(f'An error occurred: {e}')

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, record_m3u8))

    application.run_polling()

if __name__ == '__main__':
    main()
