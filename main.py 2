import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from yt_dlp import YoutubeDL

TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

bot = telebot.TeleBot(TOKEN.strip())

# Menyu buyruqlari
bot.set_my_commands([
    BotCommand("start", "Botni qayta ishga tushirish"),
    BotCommand("help", "Yordam va yoʻriqnoma"),
    BotCommand("about", "Biz haqimizda maʻlumot")
])

user_urls = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Menga YouTube havolasini yuboring, men sizga video yoki MP3 koʻrinishida yuklab beraman.")

@bot.message_handler(commands=['about'])
def send_about(message):
    bot.reply_to(message, "Ushbu bot YouTube videolarini tez va oson yuklab olish uchun yaratilgan!")

@bot.message_handler(func=lambda message: True)
def process_url(message):
    url = message.text.strip()
    if "youtu" not in url:
        bot.reply_to(message, "Iltimos, toʻgʻri YouTube havolasini yuboring.")
        return

    user_urls[message.chat.id] = url

    keyboard = InlineKeyboardMarkup()
    btn360 = InlineKeyboardButton("🎬 360p", callback_data="quality_360")
    btn480 = InlineKeyboardButton("🎬 480p", callback_data="quality_480")
    btn720 = InlineKeyboardButton("🎬 720p", callback_data="quality_720")
    btn1080 = InlineKeyboardButton("🎬 1080p", callback_data="quality_1080")
    btn_audio = InlineKeyboardButton("🎵 MP3 Audio (Faqat ovozi)", callback_data="quality_audio")
    
    keyboard.row(btn360, btn480)
    keyboard.row(btn720, btn1080)
    keyboard.row(btn_audio)

    bot.send_message(message.chat.id, "Keling, yuklash formatini tanlaymiz:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('quality_'))
def quality_selected(call):
    chat_id = call.message.chat.id
    
    if chat_id not in user_urls:
        bot.answer_callback_query(call.id, "Havola muddati tugagan. Iltimos, qayta yuboring.")
        bot.delete_message(chat_id, call.message.message_id)
        return

    url = user_urls[chat_id]
    quality = call.data.split('_')[1]
    
    is_audio = (quality == "audio")

    if is_audio:
        bot.edit_message_text("⏳ Audio (MP3) yuklanmoqda, kuting...", chat_id, call.message.message_id)
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'audio.%(ext)s',
            'max_filesize': 100000000,
            'quiet': True,
            'no_warnings': True,
        }
    else:
        bot.edit_message_text(f"⏳ {quality}p video yuklanmoqda...", chat_id, call.message.message_id)
        format_selector = f'best[height<={quality}][ext=mp4]/best'
        ydl_opts = {
            'format': format_selector,
            'outtmpl': 'video.%(ext)s',
            'max_filesize': 100000000,
            'quiet': True,
            'no_warnings': True,
            'concurrent_fragment_downloads': 5,
        }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if is_audio:
            with open(filename, 'rb') as audio_file:
                bot.send_audio(chat_id, audio_file, caption="Siz soʻragan audio fayl! 🎵")
        else:
            with open(filename, 'rb') as video_file:
                bot.send_video(chat_id, video_file, caption=f"Siz soʻragan {quality}p video! 🎬")
            
        if os.path.exists(filename):
            os.remove(filename)
        del user_urls[chat_id]
        
        bot.delete_message(chat_id, call.message.message_id)

    except Exception as e:
        bot.edit_message_text(f"Xatolik yuz berdi: {str(e)}", chat_id, call.message.message_id)
        if chat_id in user_urls:
            del user_urls[chat_id]

bot.infinity_polling(timeout=10, long_polling_timeout=5)
