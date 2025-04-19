from telebot.types import Message
from keyboards.default import main_menu
from config import SUPER_ADMINS

def register_handlers(bot):
    from handlers.shifts import register_handlers as register_shift_handlers
    from handlers.barista import register_handlers as register_barista_handlers
    from handlers.locations import register_handlers as register_location_handlers
    from handlers.staff import register_handlers as register_employee_handlers

    register_shift_handlers(bot)
    register_barista_handlers(bot)
    register_location_handlers(bot)
    register_employee_handlers(bot)

    @bot.message_handler(commands=['start'])
    def start(message: Message):
        user_id = message.from_user.id
        if user_id in SUPER_ADMINS:
            bot.send_message(message.chat.id, "Привет, админ!", reply_markup=main_menu())
        else:
            bot.send_message(message.chat.id, "Добро пожаловать в бот кофейни!", reply_markup=main_menu())
