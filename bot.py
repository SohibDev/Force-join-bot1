import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    CommandHandler, MessageHandler, filters,
    CallbackQueryHandler
)
from telegram.error import BadRequest

# 🔐 Kerakli o‘rnatmalar
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ✅ Obuna bo‘lishi kerak bo‘lgan kanallar
REQUIRED_CHANNELS = ['@urguttvrasmiy', '@josefdesign']

# 📽 Video fayllar (file_id lar)
VIDEO_FILES = {
    "kino1": "AgADPngAAp4V8Ug"  # O‘zingiznikini yozing
}

# 🔎 Obuna tekshirish funksiyasi
async def is_subscribed(user_id, bot):
    for channel in REQUIRED_CHANNELS:
        try:
            # Kanalga obuna bo'lganlik holatini tekshirish
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except BadRequest as e:
            # Xato holatini chiqarish va tekshirish
            print(f"Error checking subscription for {channel}: {e}")
            return False
    return True

# 🚀 /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bot = context.bot

    # Obuna bo'lganini tekshirish
    if not await is_subscribed(user_id, bot):
        kanal_list = "\n".join(REQUIRED_CHANNELS)

        # Tekshirish tugmasi va kanallar uchun tugmalar
        keyboard = [
            [InlineKeyboardButton(channel, url=f"https://t.me/{channel[1:]}")] for channel in REQUIRED_CHANNELS
        ]
        keyboard.append([InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_subscription")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"⛔️ Iltimos, quyidagi kanallarga obuna bo‘ling:",
            reply_markup=reply_markup
        )
        return

    await update.message.reply_text("🎬 Xush kelibsiz! Kino kodini yozing (masalan: kino1)")

# 📲 Tekshirish tugmasi bosilganda
async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    bot = context.bot

    # Foydalanuvchi tugma bosganini tekshirish
    if query.data == "check_subscription":
        # Obuna bo'lishini tekshirish
        if not await is_subscribed(user_id, bot):
            kanal_list = "\n".join(REQUIRED_CHANNELS)
            await query.answer()
            
            # Foydalanuvchiga obuna bo'lish uchun kanalga o'tish tugmalarini yuborish
            keyboard = [
                [InlineKeyboardButton(channel, url=f"https://t.me/{channel[1:]}")] for channel in REQUIRED_CHANNELS
            ]
            keyboard.append([InlineKeyboardButton("✅Obunani tekshirish", callback_data="check_subscription")])
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"⛔️ Siz hali obuna bo‘lmadingiz. Quyidagi kanallarga obuna bo‘ling:",
                reply_markup=reply_markup
            )
        else:
            await query.answer()
            await query.edit_message_text("✅ Siz obuna bo'lgansiz! Kino kodi yuboring.")

# 🧠 Har qanday matnni tekshirish va tugmalar qo‘shish
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bot = context.bot
    text = update.message.text.strip().lower()

    # Obuna bo‘lmagan foydalanuvchilar uchun
    if not await is_subscribed(user_id, bot):
        kanal_list = "\n".join(REQUIRED_CHANNELS)

        keyboard = [
            [InlineKeyboardButton(channel, url=f"https://t.me/{channel[1:]}")] for channel in REQUIRED_CHANNELS
        ]
        keyboard.append([InlineKeyboardButton("✅ Obunani tekshirish", callback_data="check_subscription")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"⛔️ Avval quyidagi kanallarga obuna bo‘ling:",
            reply_markup=reply_markup
        )
        return

    # 🎥 Kino kodi tekshirish
    if text in VIDEO_FILES:
        # Tugma va video yuborish
        keyboard = [
            [InlineKeyboardButton("Kino kodi: kino1", callback_data="kino1")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_video(video=VIDEO_FILES[text], reply_markup=reply_markup)
    else:
        await update.message.reply_text("❓ Noto‘g‘ri kod. Iltimos, 'kino1' deb yozing.")

# 🔧 Botni ishga tushirish
print("✅ Bot ishga tushdi!")
app = ApplicationBuilder().token("7201517085:AAFrR2NUxz3vdaydNclv788lZ0WeddfhxRY").build()  # ← TOKENingizni kiriting

# 🔗 Handlerlar
app.add_handler(CommandHandler('start', start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# 👀 Tekshirish tugmasi uchun callback handler
app.add_handler(CallbackQueryHandler(check_subscription, pattern="check_subscription"))

# 🚦 Polling boshlash
app.run_polling()
