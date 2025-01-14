# helpers.py

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Відображає інформацію про поточний тиждень, спринт та години.
    """
    user_data = context.user_data

    week = user_data.get("week", 1)
    sprint = user_data.get("sprint", 1)
    week_hours = user_data.get("week_hours", 0.0)
    sprint_hours = user_data.get("sprint_hours", 0.0)
    total_hours = user_data.get("total_hours", 0.0)

    text = (
        f"📆 <b>Тиждень:</b> {week}\n"
        f"🚀 <b>Спринт:</b> {sprint}\n\n"
        f"⏳ <b>Годин за тиждень:</b> {week_hours:.1f}\n"
        f"🏁 <b>Годин за спринт:</b> {sprint_hours:.1f}\n"
        f"📊 <b>Загальна кількість годин:</b> {total_hours:.1f}"
    )

    keyboard = [
        [KeyboardButton("📚 Трекати навчання")],
        [KeyboardButton("✅ Закінчити тиждень")],
        [KeyboardButton("🏆 Закінчити спринт")],
        [KeyboardButton("📈 Статистика")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    else:
        chat_id = update.callback_query.message.chat_id
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
