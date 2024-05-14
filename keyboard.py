from aiogram.types import KeyboardButton, BotCommand
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

admin_buttons = ReplyKeyboardBuilder()
admin_buttons.row(KeyboardButton(text="Category qo'shish"), KeyboardButton(text="Product qo'shish"))
admin_buttons.row(KeyboardButton(text="Category o'chirish"), KeyboardButton(text="Product o'chirish"))
admin_buttons.adjust(2, repeat=True)

c_lis = [BotCommand(command='start', description='Botni boshlash'),
         BotCommand(command='help', description='Yordam'),
         ]


def make_menu(**kwargs):
    rkb = ReplyKeyboardBuilder()
    rkb.row(KeyboardButton(text=_("📚 Books")))
    rkb.row(KeyboardButton(text=_("📃 My orders")))
    rkb.row(KeyboardButton(text=_("🔵 Our social media")), KeyboardButton(text=_("📞 Contact us")))
    rkb.row(KeyboardButton(text='🌐 Tilni almshtirish'))

    return rkb.as_markup(resize_keyboard=True)
