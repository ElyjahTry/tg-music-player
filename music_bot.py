from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import (
    ApplicationBuilder, MessageHandler, CommandHandler,
    ContextTypes, filters, ConversationHandler
)
import json
import os

TOKEN = '7653784788:AAHeNQqdYB95aeuGCcVmHl_ytTsRvFvzkk8'
DATA_FILE = 'data.json'
USER_STATE = {}  # Временное хранилище состояний пользователей

STAGE_ALBUM, STAGE_YEAR, STAGE_GENRE, STAGE_COVER = range(4)

# Если data.json не существует, создаём его
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({"tracks": []}, f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Добавляем кнопку для открытия Web App (ссылка на деплой Vercel)
    keyboard = [
        [KeyboardButton("🎧 Открыть плеер", web_app=WebAppInfo(url="https://tg-music-player-frontend.vercel.app/"))]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привет! Нажми на кнопку, чтобы открыть плеер:", reply_markup=markup)

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    audio = message.audio
    if audio:
        file_id = audio.file_id
        title = audio.title or "Без названия"
        performer = audio.performer or "Неизвестный"
        duration = audio.duration

        data = load_data()

        track = {
            "file_id": file_id,
            "title": title,
            "performer": performer,
            "duration": duration
        }

        # Сохраняем временно данные для дополнения информации
        USER_STATE[message.from_user.id] = track

        # Логирование: выводим данные трека в консоль
        print(f"Track received: {track}")

        await message.reply_text(
            f"🎶 Сохранил: {performer} – {title}\n"
            "Хочешь дополнить информацию (альбом, год, жанр, обложка)? Напиши что-нибудь, и начнём ⬇️\n"
            "Или отправь /skip чтобы пропустить"
        )
        return STAGE_ALBUM

async def skip_extra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    data = load_data()
    if user_id in USER_STATE:
        data["tracks"].append(USER_STATE[user_id])
        save_data(data)
        del USER_STATE[user_id]
    await update.message.reply_text("Окей, трек сохранён без дополнительных данных ✅")
    return ConversationHandler.END

async def get_album(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    USER_STATE[user_id]["album"] = update.message.text
    await update.message.reply_text("📅 Укажи год (например: 2022)")
    return STAGE_YEAR

async def get_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    try:
        USER_STATE[user_id]["year"] = int(update.message.text)
    except ValueError:
        USER_STATE[user_id]["year"] = None
    await update.message.reply_text("🎭 Укажи жанр (например: Rock, Pop)")
    return STAGE_GENRE

async def get_genre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    USER_STATE[user_id]["genre"] = update.message.text
    await update.message.reply_text("🖼 Теперь отправь картинку для обложки (или нажми /skip)")
    return STAGE_COVER

async def get_cover(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if update.message.photo:
        photo = update.message.photo[-1]  # Берём самую большую фотографию
        USER_STATE[user_id]["cover_file_id"] = photo.file_id
    else:
        USER_STATE[user_id]["cover_file_id"] = None

    data = load_data()
    data["tracks"].append(USER_STATE[user_id])
    save_data(data)
    del USER_STATE[user_id]

    await update.message.reply_text("✅ Трек сохранён со всеми метаданными! Спасибо :)")
    return ConversationHandler.END

async def list_tracks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    # Логируем содержимое треков для отладки
    print(f"Tracks loaded: {data['tracks']}")
    if not data["tracks"]:
        await update.message.reply_text("Нет сохранённых треков 😢")
        return

    msg = "📂 Твои треки:\n\n"
    for i, t in enumerate(data["tracks"], start=1):
        msg += f"{i}. {t.get('performer', '?')} – {t.get('title', '?')}\n"
    await update.message.reply_text(msg)

app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.AUDIO, handle_audio)],
    states={
        STAGE_ALBUM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_album)],
        STAGE_YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_year)],
        STAGE_GENRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_genre)],
        STAGE_COVER: [
            MessageHandler(filters.PHOTO, get_cover),
            CommandHandler("skip", skip_extra),
        ],
    },
    fallbacks=[CommandHandler("skip", skip_extra)],
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("tracks", list_tracks))
app.add_handler(conv_handler)

print("Бот запущен. Ждём MP3...")
app.run_polling()
