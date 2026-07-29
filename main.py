import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from yt_dlp import YoutubeDL

TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

bot = telebot.TeleBot(TOKEN.strip())

# Menyu buyruqlari (faqat start qoldirildi)
bot.set_my_commands([
    BotCommand("start", "Botni qayta ishga tushirish")
])

user_urls = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Menga YouTube havolasini yuboring.")

@bot.message_handler(func=lambda message: True)
def process_url(message):
    url = message.text.strip()
    if "youtu" not in url:
        bot.reply_to(message, "Iltimos, to‘g‘ri YouTube havolasini yuboring.")
        return

    user_urls[message.chat.id] = url

    keyboard = InlineKeyboardMarkup()
    btn360 = InlineKeyboardButton("🎬 360p", callback_data="quality_360")
    btn480 = InlineKeyboardButton("🎬 480p", callback_data="quality_480")
    btn720 = InlineKeyboardButton("🎬 720p", callback_data="quality_720")
    btn1080 = InlineKeyboardButton("🎬 1080p", callback_data="quality_1080")
    btn_audio = InlineKeyboardButton("🎵 MP3 Audio", callback_data="quality_audio")

    keyboard.row(btn360, btn480)
    keyboard.row(btn720, btn1080)
    keyboard.row(btn_audio)

    bot.send_message(message.chat.id, "Keling, yuklab olish sifatini tanlang:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('quality_'))
def quality_selected(call):
    chat_id = call.message.chat.id

    if chat_id not in user_urls:
        bot.answer_callback_query(call.id, "Havola topilmadi, qaytadan yuboring.")
        bot.delete_message(chat_id, call.message.message_id)
        return

    url = user_urls[chat_id]
    quality = call.data.split('_')[1]

    is_audio = (quality == "audio")

    if is_audio:
        status_msg = bot.edit_message_text("⏳ Audio (MP3) yuklanmoqda...", chat_id, call.message.message_id)
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'downloads/{chat_id}_%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:
        status_msg = bot.edit_message_text(f"⏳ Video ({quality}p) yuklanmoqda...", chat_id, call.message.message_id)
        ydl_opts = {
            'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]',
            'outtmpl': f'downloads/{chat_id}_%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
        }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if is_audio:
                filename = os.path.splitext(filename)[0] + '.mp3'

        with open(filename, 'rb') as file:
            if is_audio:
                bot.send_audio(chat_id, file)
            else:
                bot.send_video(chat_id, file)

        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        bot.send_message(chat_id, f"Xatolik yuz berdi: {str(e)}")

if __name__ == '__main__':
    bot.infinity_polling()
