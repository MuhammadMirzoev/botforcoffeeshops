import telebot
from handlers.base import register_handlers
from models.schema import init_db
from config import SUPER_ADMINS
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

# Инициализация базы данных
init_db()

# Регистрируем все хендлеры
register_handlers(bot)

# Запуск
print("Бот запущен...")
bot.infinity_polling()
