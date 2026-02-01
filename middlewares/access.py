from typing import Any, Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from config import ALLOWED_USER_IDS


class AccessMiddleware(BaseMiddleware):
    """
    Middleware, который проверяет user_id входящего сообщения.
    Если пользователь не входит в список ALLOWED_USER_IDS — отправляет отказ.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # Извлекаем user_id в зависимости от типа события
        user_id: int | None = None

        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        # Проверяем доступ
        if user_id is not None and user_id not in ALLOWED_USER_IDS:
            if isinstance(event, Message):
                await event.answer("У вас нет доступа к этому боту.")
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "У вас нет доступа к этому боту.", show_alert=True)
            return  # Прерываем обработку

        # Доступ есть — передаём дальше
        return await handler(event, data)
