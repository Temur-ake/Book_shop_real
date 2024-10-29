import asyncio
import logging
from aiogram import Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from filter import IsAdmin
from state import AdminState
from keyboard import show_categories, make_plus_minus, main_keyboard_btn, admin_panel_keyboard
from cons import database

logging.basicConfig(level=logging.INFO)

main_router = Router()


@main_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user_id = str(message.from_user.id)
    rkb = main_keyboard_btn()
    msg = _('Assalomu alaykum! Tanlang.')

    users = database.get('users', {})
    print(users)
    if user_id not in users:
        users[user_id] = True
        database['users'] = users
        msg = _('Assalomu alaykum! \nXush kelibsiz!')

    await message.answer(text=msg, reply_markup=rkb.as_markup(resize_keyboard=True))


@main_router.message(Command(commands='help'))
async def help_command(message: Message) -> None:
    await message.answer(_('''Buyruqlar:
/start - Botni ishga tushirish
/help - Yordam'''))


@main_router.message(F.text == __('🌐 Tilni almashtirish'))
async def change_language(message: Message) -> None:
    keyboards = InlineKeyboardBuilder()
    keyboards.row(InlineKeyboardButton(text='Uz🇺🇿', callback_data='lang_uz'),
                  InlineKeyboardButton(text='En🇬🇧', callback_data='lang_en'),
                  InlineKeyboardButton(text='Ru🇷🇺', callback_data='lang_ru'))

    await message.answer(_('Tilni tanlang: '), reply_markup=keyboards.as_markup())


@main_router.callback_query(F.data.startswith('lang_'))
async def languages(callback: CallbackQuery, state: FSMContext) -> None:
    lang_code = callback.data.split('lang_')[-1]
    await state.update_data(locale=lang_code)

    lang = _('Uzbek', locale=lang_code) if lang_code == 'uz' else \
        _('Ingiliz', locale=lang_code) if lang_code == 'en' else \
            _('Rus', locale=lang_code)

    await callback.answer(_('{lang} tili tanlandi', locale=lang_code).format(lang=lang))

    rkb = main_keyboard_btn(locale=lang_code)
    msg = _('Assalomu alaykum! Tanlang.', locale=lang_code)
    await callback.message.answer(text=msg, reply_markup=rkb.as_markup(resize_keyboard=True))


@main_router.message(F.text == __('🔵 Biz ijtimoyi tarmoqlarda'))
async def our_social_network(message: Message) -> None:
    ikb = InlineKeyboardBuilder()
    ikb.row(InlineKeyboardButton(text='IKAR | Factor Books', url='https://t.me/ikar_factor'))
    ikb.row(InlineKeyboardButton(text='Factor Books', url='https://t.me/factor_books'))
    ikb.row(InlineKeyboardButton(text='\"Factor Books\" nashiryoti', url='https://t.me/factorbooks'))
    await message.answer(_('Biz ijtimoiy tarmoqlarda'), reply_markup=ikb.as_markup())


@main_router.message(F.text == __('🛒 Mahsulotlar'))
async def books(message: Message) -> None:
    ikb = show_categories(message.from_user.id)
    await message.answer(_('Kategoriyalardan birini tanlang'), reply_markup=ikb.as_markup())


@main_router.callback_query(F.data.startswith('orqaga'))
async def back_handler(callback: CallbackQuery):
    await callback.message.edit_text(_('Kategoriyalardan birini tanlang'),
                                     reply_markup=show_categories(callback.from_user.id).as_markup())


@main_router.message(F.text == __("📞 Biz bilan bog'lanish"))
async def contact_info(message: Message) -> None:
    text = _("""\n\nTelegram: @C_W24\n📞  +{number}\n🤖 Bot Kozimov Temur (@C_W24) tomonidan tayorlandi.\n""".format(
        number=998970501655))
    await message.answer(text=text, parse_mode=ParseMode.HTML)


@main_router.callback_query()
async def product_handler(callback: CallbackQuery):
    if callback.data in database.get('categories', {}):
        ikb = InlineKeyboardBuilder()
        for k, v in database.get('products', {}).items():
            if 'category_id' in v and v['category_id'] == callback.data:
                ikb.add(InlineKeyboardButton(text=v['name'], callback_data=k))
        if str(callback.from_user.id) in database.get('basket', {}):
            ikb.add(
                InlineKeyboardButton(text=f'🛒 Savat ({len(database.get('basket', {})[str(callback.from_user.id)])})',
                                     callback_data='savat'))
        ikb.add(InlineKeyboardButton(text=_("◀️ orqaga"), callback_data='orqaga'))
        ikb.adjust(2, repeat=True)
        await callback.message.edit_text(str(database['categories'][callback.data]), reply_markup=ikb.as_markup())
    elif callback.data in database.get('products', {}):
        product = database.get('products', {})[callback.data]
        ikb = make_plus_minus(1, callback.data)
        await callback.message.delete()
        await callback.message.answer_photo(photo=product['image'], caption=product['text'],
                                            reply_markup=ikb.as_markup())


@main_router.message(F.text == "Reklama 🔊", IsAdmin())
async def admin(message: Message, state: FSMContext):
    await message.answer("Reklama rasmini kiriting !")
    await state.set_state(AdminState.photo)


@main_router.message(AdminState.photo, IsAdmin(), ~F.text, F.photo)
async def admin_photo(message: Message, state: FSMContext):
    photo = message.photo[-1].file_id
    await state.update_data({"photo": photo})
    await state.set_state(AdminState.title)
    await message.answer("Reklama haqida to'liq malumot bering !")


@main_router.message(AdminState.title, IsAdmin(), ~F.photo)
async def admin_title(message: Message, state: FSMContext):
    title = message.text
    await state.update_data({"title": title})

    data = await state.get_data()
    photo = data.get('photo')
    title = data.get('title')

    await state.clear()

    users = list(database.get('users', {}).keys())

    if not users:
        await message.answer("No users found.")
        return

    tasks = []
    count = 0
    max_tasks_per_batch = 28

    for user_id in users:
        if len(tasks) >= max_tasks_per_batch:
            await asyncio.gather(*tasks)
            tasks = []

        try:
            tasks.append(message.bot.send_photo(chat_id=user_id, photo=photo, caption=title))
            count += 1
        except Exception as e:
            logging.error(f"Error sending message to user {user_id}: {e}")

    if tasks:
        await asyncio.gather(*tasks)

    await message.answer("Reklama yuborildi!", reply_markup=admin_panel_keyboard)
    await state.set_state(AdminState.end)


@main_router.message(lambda msg: msg.text[-36:] in (database.get('products') or {}).keys())
async def answer_inline_query(message: Message):
    logging.info(f"Current database state: {database}")

    products = database.get('products', {})

    msg = message.text[-36:]
    product = products.get(msg)

    if not product:
        await message.answer("Mahsulot topilmadi.")
        return

    ikb = make_plus_minus(1, msg)
    await message.delete()
    await message.answer_photo(photo=product['image'], caption=product['text'], reply_markup=ikb.as_markup())
