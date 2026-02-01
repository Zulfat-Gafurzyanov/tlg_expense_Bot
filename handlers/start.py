from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from services import expense_service

router = Router()


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    """Обработчик команды /start — приветствие и список команд."""
    month_label = expense_service.get_month_label()

    text = (
        f"👋 Привет! Добро пожаловать в бот контроля расходов.\n"
        f"📅 Текущий месяц: <b>{month_label}</b>\n\n"
        f"Доступные команды:\n"
        f"  /add — добавить расход\n"
        f"  /list — просмотр расходов\n"
        f"  /edit — редактировать запись\n"
        f"  /delete — удалить запись\n"
        f"  /export — экспорт файла"
    )

    await message.answer(text, parse_mode="HTML")
