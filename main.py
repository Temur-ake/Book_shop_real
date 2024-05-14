import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from routers.admin import admin_router
from routers.cons import TOKEN, database
from routers.handlers import user_router
from routers.inline_mode import inline_router

dp = Dispatcher()


async def on_startup(bot: Bot):
    if not database.get('categories'):
        database['categories'] = {}

    if not database.get('products'):
        database['products'] = {}

    if not database.get('users'):
        database['users'] = {}
    if not database.get('basket'):
        database['basket'] = {}
    if not database.get('order_status'):
        database['order_status'] = ('✅ accepted', '🔄 in standby mode')
    if not database.get('order_count'):
        database['order_count'] = 0

    c_lis = [BotCommand(command='start', description='Botni boshlash'),
             BotCommand(command='help', description='Yordam'),
             ]

    await bot.set_my_commands(c_lis)


async def on_shutdown(bot: Bot):
    await bot.delete_my_commands()


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.include_routers(admin_router, user_router, inline_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
