from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from helpers import show_main_menu  # Імпортуємо show_main_menu із helpers.py
from database.db import add_user
from handlers.stats_handlers import show_statistics  # Додаємо імпорт для статистики


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Відображає інформацію про поточний тиждень, спринт та години з покращеним дизайном.
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
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        chat_id = update.callback_query.message.chat_id
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode="HTML")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Команда /start
    1. Реєструє користувача (якщо новий).
    2. Ініціалізує лічильники в user_data.
    3. Відкриває головне меню.
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "Anon"
    add_user(user_id, username)

    # Ініціалізуємо дані про тиждень, спринт, години
    user_data = context.user_data
    user_data["week"] = 1
    user_data["sprint"] = 1
    user_data["week_hours"] = 0.0
    user_data["sprint_hours"] = 0.0
    user_data["total_hours"] = 0.0

    await show_main_menu(update, context)


async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обробляє натискання кнопок з головного меню та текстові команди.
    """
    text = update.message.text
    user_data = context.user_data

    if text in ["📚 Трекати навчання", "Трекати навчання"]:
        await update.message.reply_text("Скільки годин ви витратили? Введіть число:")
        context.user_data["awaiting_hours"] = True  # Вказуємо, що очікуємо введення годин

    elif context.user_data.get("awaiting_hours"):
        context.user_data["awaiting_hours"] = False  # Знімаємо очікування
        await handle_hours_input(update, context)

    elif text in ["✅ Закінчити тиждень", "Закінчити тиждень"]:
        user_data["week"] = user_data.get("week", 1) + 1
        user_data["week_hours"] = 0.0
        await show_main_menu(update, context)

    elif text in ["🏆 Закінчити спринт", "Закінчити спринт"]:
        user_data["sprint"] = user_data.get("sprint", 1) + 1
        user_data["week"] = 1
        user_data["week_hours"] = 0.0
        user_data["sprint_hours"] = 0.0
        await show_main_menu(update, context)

    elif text in ["📈 Статистика", "Статистика"]:
        await show_statistics(update, context)

    else:
        await update.message.reply_text("Невідома дія. Оберіть кнопку з меню.")


async def handle_hours_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обробляє введення годин для навчання.
    """
    user_data = context.user_data

    try:
        # Конвертуємо введення в число
        hours = float(update.message.text)
        user_data["week_hours"] = user_data.get("week_hours", 0.0) + hours
        user_data["sprint_hours"] = user_data.get("sprint_hours", 0.0) + hours
        user_data["total_hours"] = user_data.get("total_hours", 0.0) + hours

        await update.message.reply_text(f"Збережено {hours} годин.")
        await show_main_menu(update, context)
    except ValueError:
        # Виводимо повідомлення про помилку
        await update.message.reply_text("Помилка! Будь ласка, введіть число для годин.")
