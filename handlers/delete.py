from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services import expense_service


class DeleteExpense(StatesGroup):
    """Состояние ожидания ввода ID для удаления."""
    wait_id = State()


router = Router()


@router.message(Command("delete"))
async def handle_delete_start(message: Message, state: FSMContext) -> None:
    """Начало сценария удаления — просим ввести ID записи."""
    expenses = expense_service.get_all_expenses()
    if not expenses:
        await message.answer("📋 Пока нет записей для удаления.")
        return

    await state.set_state(DeleteExpense.wait_id)
    await message.answer("🗑️ Введите ID записи для удаления (например: 1):")


@router.message(DeleteExpense.wait_id)
async def handle_delete_id(message: Message, state: FSMContext) -> None:
    """Обработчик ввода ID — валидация и удаление."""
    text = message.text.strip()

    if not text.isdigit() or int(text) <= 0:
        await message.answer("❌ Введите корректный ID (целое положительное число):")
        return

    expense_id = int(text)
    success = expense_service.delete_expense(expense_id)

    if not success:
        await state.clear()
        await message.answer(f"❌ Запись с ID #{expense_id} не найдена.")
        return

    await state.clear()
    await message.answer(f"🗑️ Запись #{expense_id} удалена.")