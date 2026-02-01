from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services import expense_service

router = Router()


@router.message(Command("list"))
async def handle_list(message: Message) -> None:
    """Отправляет текстовый список всех записей текущего месяца."""
    expenses = expense_service.get_all_expenses()

    if not expenses:
        await message.answer("📋 Пока нет записей за этот месяц.")
        return

    month_label = expense_service.get_month_label()

    lines = [f"📋 Расходы за <b>{month_label}</b>:\n"]
    for exp in expenses:
        line = f"  #{exp['id']} | {exp['date']} | {exp['category']} | {exp['amount']:.2f} руб."
        # Добавляем комментарий если он есть
        if exp["comment"]:
            line += f"\n       💬 {exp['comment']}"
        lines.append(line)

    await message.answer("\n".join(lines), parse_mode="HTML")