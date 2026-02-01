from config import CATEGORIES
from repository import excel_repo


# --- Валидация ---


def is_valid_category(category: str) -> bool:
    """Проверяет, входит ли категория в предопределённый список."""
    return category in CATEGORIES


def parse_amount(text: str) -> float | None:
    """
    Парсит строку в число (float).
    Возвращает None если строка не является валидным числом.
    Поддержка запятой как разделителя десятичной части.
    """
    try:
        cleaned = text.strip().replace(",", ".")
        value = float(cleaned)
        if value <= 0:
            return None
        return value
    except ValueError:
        return None


# --- Бизнес-логика ---


def add_expense(category: str, amount: float, comment: str | None = None) -> int:
    """
    Валидирует и сохраняет новый расход через репозиторий.
    Возвращает ID созданной записи.
    """
    if not is_valid_category(category):
        raise ValueError(f"Недопустимая категория: {category}")
    if amount <= 0:
        raise ValueError("Сумма должна быть положительной")

    return excel_repo.add_expense(category=category, amount=amount, comment=comment)


def get_all_expenses() -> list[dict]:
    """Возвращает все записи текущего месяца."""
    return excel_repo.get_all_expenses()


def delete_expense(expense_id: int) -> bool:
    """Удаляет запись по ID. Возвращает True если удалена успешно."""
    return excel_repo.delete_expense(expense_id)


def update_category(expense_id: int, new_category: str) -> bool:
    """Обновляет категорию записи. Возвращает True если обновление успешно."""
    if not is_valid_category(new_category):
        raise ValueError(f"Недопустимая категория: {new_category}")
    return excel_repo.update_expense_category(expense_id, new_category)


def update_amount(expense_id: int, new_amount: float) -> bool:
    """Обновляет сумму записи. Возвращает True если обновление успешно."""
    if new_amount <= 0:
        raise ValueError("Сумма должна быть положительной")
    return excel_repo.update_expense_amount(expense_id, new_amount)


def update_comment(expense_id: int, new_comment: str) -> bool:
    """Обновляет комментарий записи. Возвращает True если обновление успешно."""
    return excel_repo.update_expense_comment(expense_id, new_comment)


def get_month_label() -> str:
    """Возвращает метку текущего месяца для отображения в боте."""
    return excel_repo.get_current_month_label()