from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from config import CATEGORIES
from services import expense_service
from states import AddExpense

router = Router()


def _build_category_keyboard() -> InlineKeyboardMarkup:
    """Создаёт inline-клавиатуру с категориями расходов."""
    buttons = [
        [InlineKeyboardButton(text=cat, callback_data=f"add_cat:{cat}")]
        for cat in CATEGORIES
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(Command("add"))
async def handle_add_start(message: Message, state: FSMContext) -> None:
    """Начало сценария добавления расхода — просим выбрать категорию."""
    await state.set_state(AddExpense.wait_category)
    await message.answer(
        "📂 Выберите категорию расхода:",
        reply_markup=_build_category_keyboard(),
    )


@router.callback_query(F.data.startswith("add_cat:"), AddExpense.wait_category)
async def handle_add_category(callback: CallbackQuery, state: FSMContext) -> None:
    """Обработчик выбора категории через inline-кнопку."""
    category = callback.data.split(":", 1)[1]

    await state.update_data(category=category)
    await state.set_state(AddExpense.wait_amount)

    await callback.message.edit_text(
        f"📂 Категория: <b>{category}</b>",
        parse_mode="HTML",
    )
    await callback.answer()
    await callback.message.answer("💰 Введите сумму расхода (например: 350 или 120.50):")


@router.message(AddExpense.wait_amount)
async def handle_add_amount(message: Message, state: FSMContext) -> None:
    """Обработчик ввода суммы — валидация, переход к комментарию."""
    amount = expense_service.parse_amount(message.text)

    if amount is None:
        await message.answer("❌ Некорректная сумма. Введите число (например: 350 или 120.50):")
        return

    # Сохраняем сумму в FSM и переходим к комментарию
    await state.update_data(amount=amount)
    await state.set_state(AddExpense.wait_comment)

    await message.answer(
        "💬 Добавьте комментарий к расходу (или /skip, чтобы пропустить):"
    )


@router.message(AddExpense.wait_comment)
async def handle_add_comment(message: Message, state: FSMContext) -> None:
    """Обработчик ввода комментария (или /skip для пропуска) — сохранение записи."""
    data = await state.get_data()
    category = data["category"]
    amount = data["amount"]

    # Определяем комментарий: /skip означает пустой
    comment = None if message.text.strip().lower() == "/skip" else message.text.strip()

    # Сохраняем расход, получаем ID
    new_id = expense_service.add_expense(category=category, amount=amount, comment=comment)

    # Сбрасываем состояние
    await state.clear()

    # Формируем подтверждение с ID
    text = f"✅ Расход добавлен (ID: #{new_id})\n{category} — {amount:.2f} руб."
    if comment:
        text += f"\n💬 {comment}"

    await message.answer(text)