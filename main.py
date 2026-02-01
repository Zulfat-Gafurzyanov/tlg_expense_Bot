import asyncio

from aiogram import Dispatcher, Bot

from config import TELEGRAM_BOT_TOKEN
from middlewares.access import AccessMiddleware
from middlewares.fsm_reset import FSMResetMiddleware
from handlers import start, add, list as list_handler, delete, edit, export, echo


async def main() -> None:
    """Точка входа: инициализация бота, регистрация middleware и роутеров."""

    # Инициализация бота и диспетчера
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    # FSMResetMiddleware идёт первым: если пользователь внутри сценария и набрал /команду,
    # состояние сбрасывается и команда идёт в свой хендлер а не в текущий FSM-обработчик
    dp.message.middleware.register(FSMResetMiddleware())

    # Регистрируем middleware доступа на Message и CallbackQuery
    dp.message.middleware.register(AccessMiddleware())
    dp.callback_query.middleware.register(AccessMiddleware())

    # Регистрируем роутеры хендлеров
    dp.include_router(start.router)
    dp.include_router(add.router)
    dp.include_router(list_handler.router)
    dp.include_router(delete.router)
    dp.include_router(edit.router)
    dp.include_router(export.router)

    # Echo идёт последним — ловит всё что не обработало остальное
    dp.include_router(echo.router)

    # Удаляем старые обновления при старте (чтобы бот не обрабатывал сообщения из прошлого)
    await bot.delete_webhook(drop_pending_updates=True)

    print("✅ Бот запущен. Ожидаем сообщения...")

    # Запускаем polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())