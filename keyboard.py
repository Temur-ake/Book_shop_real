from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, BotCommand
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from cons import database

admin_panel_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Product qoshish'), KeyboardButton(text='Category qoshish')],
              [KeyboardButton(text='Delete category'), KeyboardButton(text='Delete product')],
              [KeyboardButton(text='🛒 Mahsulotlar'), KeyboardButton(text='Reklama 🔊')]
              ],
    resize_keyboard=True)


def show_categories(user_id):
    ikb = InlineKeyboardBuilder()
    for k, v in database.get('categories', {}).items():
        ikb.add(InlineKeyboardButton(text=str(v), callback_data=k))
    ikb.add(InlineKeyboardButton(text=_('🔍 Qidirish'), switch_inline_query_current_chat=''))
    if str(user_id) in database.get('basket', {}):
        ikb.add(InlineKeyboardButton(text=f'🛒 Savat ({len(database["basket"][str(user_id)])})', callback_data='savat'))
    ikb.adjust(2, repeat=True)
    return ikb


def make_plus_minus(quantity, product_id):
    ikb = InlineKeyboardBuilder()
    ikb.row(InlineKeyboardButton(text="➖", callback_data="change-" + product_id),
            InlineKeyboardButton(text=str(quantity), callback_data="number"),
            InlineKeyboardButton(text="➕", callback_data="change+" + product_id)
            )
    ikb.row(InlineKeyboardButton(text=_("◀️Orqaga"), callback_data="categoryga"),
            InlineKeyboardButton(text=_('🛒 Savatga qo\'shish'), callback_data="savatga" + product_id + str(quantity)))
    return ikb


def main_keyboard_btn(**kwargs):
    main_keyboard = ReplyKeyboardBuilder()
    main_keyboard.row(KeyboardButton(text=_('🛒 Mahsulotlar', **kwargs)))
    main_keyboard.row(KeyboardButton(text=_('📃 Mening buyurtmalarim', **kwargs)))
    main_keyboard.row(KeyboardButton(text=_('🔵 Biz ijtimoyi tarmoqlarda', **kwargs)),
                      KeyboardButton(text=_('📞 Biz bilan bog\'lanish', **kwargs)))
    main_keyboard.row(KeyboardButton(text=_('🌐 Tilni almashtirish', **kwargs)))
    return main_keyboard


c_lis = [
    BotCommand(command='start', description='Botni boshlash'),
    BotCommand(command='help', description='Yordam'),
]
