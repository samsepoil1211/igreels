import os
import logging
import instaloader
from flask import Flask, request
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)

# Telegram bot token
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# Instaloader instance
loader = instaloader.Instaloader()

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Send me an Instagram URL to download the video or reel.')

def download_video(update: Update, context: CallbackContext) -> None:
    url = update.message.text.strip()
    try:
        # Extract shortcode from URL
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        # Define the filename
        filename = f"{shortcode}.mp4"
        loader.download_post(post, target=filename)

        # Send the video file to Telegram
        with open(filename, 'rb') as video_file:
            update.message.reply_video(video_file)

        os.remove(filename)  # Clean up the file after sending
    except Exception as e:
        update.message.reply_text(f"Error: {str(e)}")

def main() -> None:
    updater = Updater(TELEGRAM_TOKEN)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download_video))

    updater.start_polling()
    updater.idle()

@app.route('/webhook', methods=['POST'])
def webhook():
    json_data = request.get_json()
    update = Update.de_json(json_data, bot)
    dp.process_update(update)
    return 'ok'

if __name__ == '__main__':
    main()
