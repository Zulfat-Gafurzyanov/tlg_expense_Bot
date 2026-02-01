from aiogram.fsm.state import State, StatesGroup


class AddExpense(StatesGroup):
    """Состояния для сценария добавления нового расхода."""
    wait_category = State()   # Ожидаем выбор категории
    wait_amount = State()     # Ожидаем ввод суммы
    wait_comment = State()    # Ожидаем комментарий (или /skip)


class EditExpense(StatesGroup):
    """Состояния для сценария редактирования существующей записи."""
    wait_id = State()           # Ожидаем ввод ID записи
    wait_field = State()        # Ожидаем выбор поля
    wait_new_category = State() # Ожидаем новую категорию
    wait_new_amount = State()   # Ожидаем новую сумму
    wait_new_comment = State()  # Ожидаем новый комментарий