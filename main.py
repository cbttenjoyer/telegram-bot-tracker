import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import TOKEN
from database.db import init_db
from handlers.base_handlers import start_command, handle_main_menu
from handlers.logging_handlers import get_logging_conversation_handler
from handlers.stats_handlers import show_statistics, show_category_logs

def main():
    # Логування
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # Ініціалізуємо БД
    init_db()

    # Створюємо Application
    app = ApplicationBuilder().token(TOKEN).build()

    # Додаємо ConversationHandler для трекінгу навчання
    app.add_handler(get_logging_conversation_handler())

    # Додаємо обробник головного меню
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu))

    # Додаємо команду /start
    app.add_handler(CommandHandler("start", start_command))

    # Додаємо обробники для статистики
    app.add_handler(CommandHandler("statistics", show_statistics))  # Команда для статистики
    app.add_handler(CallbackQueryHandler(show_category_logs, pattern="^stats_"))  # Callback для вибору категорії

    # Запускаємо бота
    app.run_polling()

if __name__ == "__main__":
    main()
