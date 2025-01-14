from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)
from database.db import log_learning_time
from datetime import datetime
from helpers import show_main_menu  # Імпортуємо show_main_menu з helpers.py

CATEGORY, HOURS, NOTE = range(3)  # Етапи діалогу


async def choose_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Початок діалогу. Пропонуємо категорії для трекінгу з емодзі.
    """
    keyboard = [
        [InlineKeyboardButton("🐍 Python", callback_data='Python')],
        [InlineKeyboardButton("🤖 Prompt Engineering", callback_data='Prompt Engineering')],
        [InlineKeyboardButton("🧠 Psy", callback_data='Psy')],
        [InlineKeyboardButton("🎓 UCU", callback_data='UCU')],
        [InlineKeyboardButton("📝 Інше", callback_data='Інше')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📌 <b>Оберіть категорію:</b>", reply_markup=reply_markup, parse_mode="HTML")
    return CATEGORY


async def category_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обробляємо вибір категорії.
    """
    query = update.callback_query
    await query.answer()
    context.user_data["category"] = query.data
    await query.message.edit_text(text=f"Ви обрали категорію: {query.data}.\nСкільки годин витрачено?")
    return HOURS


async def hours_entered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Запитуємо в користувача кількість годин навчання.
    """
    hours_str = update.message.text
    try:
        hours = float(hours_str.replace(",", "."))
    except ValueError:
        await update.message.reply_text("Будь ласка, введіть число (години). Спробуйте ще раз.")
        return HOURS

    context.user_data["hours"] = hours
    await update.message.reply_text("Додайте коротку замітку або введіть /skip, щоб пропустити:")
    return NOTE


async def note_entered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Обробляємо введену нотатку та зберігаємо дані.
    """
    note = update.message.text
    await save_learning_record(update, context, note)
    return ConversationHandler.END


async def skip_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Пропуск нотатки.
    """
    await save_learning_record(update, context, "")
    return ConversationHandler.END


async def save_learning_record(update: Update, context: ContextTypes.DEFAULT_TYPE, note: str):
    """
    Збереження даних у базу та оновлення головного меню.
    """
    category = context.user_data.get("category", "Інше")
    hours = context.user_data.get("hours", 0.0)
    user_id = update.effective_user.id

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_learning_time(user_id, category, hours, note, now_str)

    # Оновлюємо дані у user_data
    context.user_data["week_hours"] = context.user_data.get("week_hours", 0.0) + hours
    context.user_data["sprint_hours"] = context.user_data.get("sprint_hours", 0.0) + hours
    context.user_data["total_hours"] = context.user_data.get("total_hours", 0.0) + hours

    await update.message.reply_text("Ваш час навчання успішно збережений!")
    await show_main_menu(update, context)


def get_logging_conversation_handler() -> ConversationHandler:
    """
    Повертає ConversationHandler для трекінгу навчання.
    """
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("Трекати навчання"), choose_category)],
        states={
            CATEGORY: [CallbackQueryHandler(category_chosen)],
            HOURS: [MessageHandler(filters.TEXT & ~filters.COMMAND, hours_entered)],
            NOTE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, note_entered),
                CommandHandler('skip', skip_note)
            ],
        },
        fallbacks=[],
        per_message=False
    )
