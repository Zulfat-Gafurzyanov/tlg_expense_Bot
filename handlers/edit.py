from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from config import CATEGORIES
from services import expense_service
from states import EditExpense

router = Router()


def _build_field_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора поля для редактирования (категория, сумма, комментарий)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Категория", callback_data="edit_field:category"),
            InlineKeyboardButton(text="Сумма", callback_data="edit_field:amount"),
        ],
        [
            InlineKeyboardButton(text="Комментарий", callback_data="edit_field:comment"),
        ],
    ])


def _build_category_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора новой категории."""
    buttons = [
        [InlineKeyboardButton(text=cat, callback_data=f"edit_cat:{cat}")]
        for cat in CATEGORIES
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(Command("edit"))
async def handle_edit_start(message: Message, state: FSMContext) -> None:
    """Начало сценария редактирования — просим ввести ID записи."""
    expenses = expense_service.get_all_expenses()
    if not expenses:
        await message.answer("📋 Пока нет записей для редактирования.")
        return

    await state.set_state(EditExpense.wait_id)
    await message.answer("✏️ Введите ID записи для редактирования (например: 1):")


@router.message(EditExpense.wait_id)
async def handle_edit_id(message: Message, state: FSMContext) -> None:
    """Обработчик ввода ID — проверяем существование и просим выбрать поле."""
    text = message.text.strip()

    if not text.isdigit() or int(text) <= 0:
        await message.answer("❌ Введите корректный ID (целое положительное число):")
        return

    expense_id = int(text)

    expenses = expense_service.get_all_expenses()
    exists = any(exp["id"] == expense_id for exp in expenses)

    if not exists:
        await state.clear()
        await message.answer(f"❌ Запись с ID #{expense_id} не найдена.")
        return

    await state.update_data(expense_id=expense_id)
    await state.set_state(EditExpense.wait_field)

    await message.answer(
        f"📝 Что редактировать в записи #{expense_id}?",
        reply_markup=_build_field_keyboard(),
    )


@router.callback_query(F.data.startswith("edit_field:"), EditExpense.wait_field)
async def handle_edit_field(callback: CallbackQuery, state: FSMContext) -> None:
    """Обработчик выбора поля (категория, сумма или комментарий)."""
    field = callback.data.split(":", 1)[1]

    await callback.answer()

    if field == "category":
        await state.set_state(EditExpense.wait_new_category)
        # Заменяем кнопки поля на кнопки категорий в том же сообщении
        await callback.message.edit_text(
            "📂 Выберите новую категорию:",
            reply_markup=_build_category_keyboard(),
        )
    elif field == "amount":
        await state.set_state(EditExpense.wait_new_amount)
        # Убираем кнопки, оставляем только текст
        await callback.message.edit_text("💰 Введите новую сумму (например: 350 или 120.50):")
    elif field == "comment":
        await state.set_state(EditExpense.wait_new_comment)
        await callback.message.edit_text("💬 Введите новый комментарий (или /skip, чтобы очистить):")


@router.callback_query(F.data.startswith("edit_cat:"), EditExpense.wait_new_category)
async def handle_edit_new_category(callback: CallbackQuery, state: FSMContext) -> None:
    """Обработчик выбора новой категории."""
    new_category = callback.data.split(":", 1)[1]
    data = await state.get_data()
    expense_id = data["expense_id"]

    success = expense_service.update_category(expense_id, new_category)

    await callback.answer()

    if success:
        await state.clear()
        await callback.message.edit_text(f"✏️ Запись #{expense_id} обновлена. Категория: <b>{new_category}</b>", parse_mode="HTML")
    else:
        await callback.message.answer("❌ Не удалось обновить запись.")


@router.message(EditExpense.wait_new_amount)
async def handle_edit_new_amount(message: Message, state: FSMContext) -> None:
    """Обработчик ввода новой суммы."""
    new_amount = expense_service.parse_amount(message.text)

    if new_amount is None:
        await message.answer("❌ Некорректная сумма. Введите число (например: 350 или 120.50):")
        return

    data = await state.get_data()
    expense_id = data["expense_id"]

    success = expense_service.update_amount(expense_id, new_amount)

    if success:
        await state.clear()
        await message.answer(f"✏️ Запись #{expense_id} обновлена.")
    else:
        await message.answer("❌ Не удалось обновить запись.")


@router.message(EditExpense.wait_new_comment)
async def handle_edit_new_comment(message: Message, state: FSMContext) -> None:
    """Обработчик ввода нового комментария (/skip для очистки)."""
    data = await state.get_data()
    expense_id = data["expense_id"]

    # /skip очищает комментарий
    new_comment = "" if message.text.strip().lower() == "/skip" else message.text.strip()

    success = expense_service.update_comment(expense_id, new_comment)

    if success:
        await state.clear()
        if new_comment:
            await message.answer(f"✏️ Запись #{expense_id} обновлена.")
        else:
            await message.answer(f"✏️ Комментарий к записи #{expense_id} очищен.")
    else:
        await message.answer("❌ Не удалось обновить запись.")