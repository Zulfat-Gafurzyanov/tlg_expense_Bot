from typing import Any, Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.fsm.context import FSMContext


# Команды бота которые должны прерывать любой текущий FSM-сценарий
INTERRUPTIBLE_COMMANDS = {"/add", "/edit", "/delete", "/list", "/export", "/start"}


class FSMResetMiddleware(BaseMiddleware):
    """
    Middleware, который перехватывает /команды пока пользователь внутри FSM-сценария.
    Если пользователь в каком-то состоянии и отправляет одну из наших команд —
    состояние сбрасывается, и сообщение идёт дальше как обычная команда.
    Без этого aiogram маршрутизирует текст в текущий FSM-обработчик,
    и команда никогда не достигает своего Command-хендлера.
    """

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        # Работаем только с текстовыми сообщениями
        if not event.text:
            return await handler(event, data)

        # Проверяем: текст — это одна из наших команд?
        command = event.text.strip().split()[0].lower()
        if command not in INTERRUPTIBLE_COMMANDS:
            return await handler(event, data)

        # Если есть активное FSM-состояние — сбрасываем его
        fsm_context: FSMContext = data.get("state")
        if fsm_context:
            current_state = await fsm_context.get_state()
            if current_state is not None:
                await fsm_context.clear()

        # Пропускаем сообщение дальше — теперь оно пойдёт в Command-хендлер
        return await handler(event, data)
