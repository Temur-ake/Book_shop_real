from aiogram import F, Router
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import locale
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, \
    KeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _, lazy_gettext as __

from cons import database
from keyboard import show_categories, make_plus_minus, main_keyboard_btn

basket_router = Router()
locale.setlocale(locale.LC_ALL, '')


def basket_msg(user_id, database):
    basket_of_user = database.get('basket', {})[str(user_id)]
    msg = f'🛒 Savat \n\n'
    all_sum = 0
    for i, v in enumerate(basket_of_user.values()):
        if 'price' in v and 'quantity' in v:
            pr = float(v['price'])
            summa = int(v['quantity']) * pr
            msg += f'{i + 1}. {v["product_name"]} \n{v["quantity"]} x {v["price"]} = {str(summa)} so\'m\n\n'
            all_sum += summa
        elif 'price' not in v and 'quantity' not in v:
            msg += f'{i + 1}. {v["product_name"]} \nQuantity: Not available\nPrice: Not available\n\n'
        elif 'price' not in v:
            msg += f'{i + 1}. {v["product_name"]} \nQuantity: {v["quantity"]} \nPrice: Not available\n\n'
        elif 'quantity' not in v:
            msg += f'{i + 1}. {v["product_name"]} \nQuantity: Not available\nPrice: {v["price"]}\n\n'
    msg += f'Jami: {all_sum} so\'m'
    return msg


@basket_router.callback_query(F.data.startswith('categoryga'))
async def to_category(callback: CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(_('Kategoriyalardan birini tanlang'),
                                  reply_markup=show_categories(callback.from_user.id).as_markup())


@basket_router.callback_query(F.data.startswith('savatga'))
async def to_basket(callback: CallbackQuery):
    basket_ = database.get('basket', {})
    user = basket_.get(str(callback.from_user.id))
    product_id = callback.data[7:43]
    product = database.get('products', {})[product_id]
    if user:
        if user.get(product_id):
            user[product_id]['quantity'] += int(callback.data[43:])
        else:
            user[product_id] = {
                'product_name': product['name'],
                'quantity': callback.data[43:],
                'price': product['price']
            }
    else:
        basket_[str(callback.from_user.id)] = {
            product_id: {
                'product_name': product['name'],
                'quantity': int(callback.data[43:]),
                'price': product['price']
            }
        }
    database['basket'] = basket_
    await to_category(callback)


quantity = 1


@basket_router.callback_query(F.data.startswith("change"))
async def change_plus(callback: CallbackQuery):
    global quantity
    if callback.data.startswith("change+"):
        quantity += 1
    elif quantity < 2:
        await callback.answer(_('Eng kamida 1 ta mahsulot buyurtma qilishingiz mumkin! 😊'), show_alert=True)
        return
    else:
        quantity -= 1
    ikb = make_plus_minus(quantity, callback.data[7:])
    await callback.message.edit_reply_markup(str(callback.message.message_id), reply_markup=ikb.as_markup())


@basket_router.callback_query(F.data.startswith('savat'))
async def basket(callback: CallbackQuery):
    msg = basket_msg(callback.from_user.id, database)
    ikb = InlineKeyboardBuilder()
    ikb.row(InlineKeyboardButton(text=_('❌ Savatni tozalash'), callback_data='clear'))
    ikb.row(InlineKeyboardButton(text=_('✅ Buyurtmani tasdiqlash'), callback_data='confirm'))
    ikb.row(InlineKeyboardButton(text=_('◀️ orqaga'), callback_data='categoryga'))
    await callback.message.edit_text(msg, reply_markup=ikb.as_markup())
