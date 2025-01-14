from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database.db import get_category_stats, get_logs_by_category


async def show_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Показує кількість годин за кожною категорією.
    """
    user_id = update.effective_user.id
    stats = get_category_stats(user_id)

    if not stats:
        await update.message.reply_text("❌ <b>Немає даних для відображення статистики.</b>", parse_mode="HTML")
        return

    text = "📊 <b>Кількість годин за категоріями:</b>\n\n"
    buttons = []

    for category, hours in stats.items():
        text += f"• {category}: {hours:.1f} год.\n"
        buttons.append([InlineKeyboardButton(f"📜 {category}", callback_data=f"stats_{category}")])

    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="HTML")


async def show_category_logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Показує всі логи для обраної категорії.
    """
    query = update.callback_query
    await query.answer()

    category = query.data.split("_")[1]
    user_id = query.from_user.id
    logs = get_logs_by_category(user_id, category)

    if not logs:
        await query.message.reply_text(f"❌ <b>Немає логів для категорії {category}.</b>", parse_mode="HTML")
        return

    text = f"📜 <b>Логи для категорії {category}:</b>\n\n"
    for log in logs:
        text += f"• {log['date']} — {log['hours']} год.\n  <i>{log['note']}</i>\n\n"

    await query.message.reply_text(text, parse_mode="HTML")
