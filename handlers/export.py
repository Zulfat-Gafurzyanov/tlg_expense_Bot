from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

from repository import excel_repo
from services import expense_service

router = Router()


@router.message(Command("export"))
async def handle_export(message: Message) -> None:
    """Отправляет файл expenses.xlsx как документ в Telegram."""
    filepath = excel_repo.get_file_path()

    # Проверяем что файл существует и в нём есть хотя бы записи за текущий месяц
    if not filepath.exists():
        await message.answer("📋 Нет данных для экспорта.")
        return

    expenses = expense_service.get_all_expenses()
    if not expenses:
        await message.answer("📋 Нет данных для экспорта за этот месяц.")
        return

    # Отправляем файл как документ
    input_file = FSInputFile(path=filepath, filename="expenses.xlsx")

    await message.answer_document(
        document=input_file,
        caption=f"📤 Экспорт расходов (текущий месяц: {expense_service.get_month_label()})",
    )