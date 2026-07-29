import os
import telebot
import yt_dlp

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Assalomu alaykum! YouTube video yoki Shorts havolasini yuboring.",
    )


def download_youtube_video(url, output_path="video.mp4"):
    ydl_opts = {
        "format": "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": output_path,
        "quiet": True,
        "no_warnings": True,
        # YouTube datacenter bloklarini aylanib o'tuvchi eng muhim sozlamalar:
        "extractor_args": {
            "youtube": {
                "player_client": ["ios", "android", "mweb"],
                "skip": ["hls", "dash"],
            }
        },
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text.strip()

    if not ("youtube.com" in url or "youtu.be" in url):
        bot.reply_to(message, "Iltimos, faqat YouTube video havolasini yuboring!")
        return

    msg = bot.reply_to(message, "⏳ Video tayyorlanmoqda, kuting...")
    file_path = f"video_{message.chat.id}.mp4"

    try:
        bot.edit_message_text(
            "🚀 Video yuklab olinmoqda...", message.chat.id, msg.message_id
        )

        # Videoni yt-dlp orqali yuklash
        download_youtube_video(url, file_path)

        # Telegram'ga yuborish
        with open(file_path, "rb") as video_file:
            bot.send_video(
                message.chat.id,
                video_file,
                caption="🤖 @SaveMedia_bot orqali yuklandi",
            )

        bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(
            f"❌ Xatolik yuz berdi: {str(e)}", message.chat.id, msg.message_id
        )

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


if __name__ == "__main__":
    bot.infinity_polling()
