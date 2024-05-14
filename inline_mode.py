from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, \
    InputTextMessageContent

from routers.cons import database

inline_router = Router()


@inline_router.inline_query()
async def user_inline_handler(inline_query: InlineQuery):
    if inline_query.query == "":
        inline_list = []
        for i, (k, v) in enumerate(database.get('products').items()):
            inline_list.append(InlineQueryResultArticle(
                id=k,
                title=v['product_name'],
                input_message_content=InputTextMessageContent(
                    message_text=f"<i>{v['product_description']}</i>Buyurtma qilish uchun  : @temurs_book_shop_bot\n\nbook_id: {k}"
                ),
                thumbnail_url=v['product_thumbnail_url'],
                description=f"Factor Books\n💵 Narxi: {v['price']} so'm",
            ))
            if i == 50:
                break

        await inline_query.answer(inline_list, cache_time=5)
    else:
        products = {k: v for (k, v) in database['products'].items() if inline_query.query.lower() in v['product_name']}
        inline_list = []
        for i, (k, v) in enumerate(database['products'].items()):
            inline_list.append(InlineQueryResultArticle(
                id=k,
                title=v['product_name'],
                input_message_content=InputTextMessageContent(
                    message_text=f"<i>{v['product_description']}</i>Buyurtma qilish uchun  : @temurs_book_shop_bot: {k}"
                ),
                thumbnail_url=v['thumbnail_url'],
                description=f"Factor Books\n💵 Narxi: {v['product_price']} so'm",
            ))
            if i == 50:
                break

        await inline_query.answer(inline_list, cache_time=5)
