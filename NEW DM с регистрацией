import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext

# =================== ВСТАВЬ СВОИ ДАННЫЕ ===================
BOT_TOKEN = "8385165542:AAGnUqMG_NkNl6KFhzjFk4QYQ__BOpKK9CY"
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwz3y6XYpSqIs3lL5vEj16qVLLyNVrIkS_RwaT-njuaUsWUGXseVr5vVg3WFyOkqM62YA/exec"
# ============================================================

logging.basicConfig(level=logging.INFO)

# Создаём бота и диспетчер с памятью состояний
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# FSM состояния
class Form(StatesGroup):
    fio = State()
    position = State()
    department = State()
    suggestion = State()

# Словарь для хранения временных данных пользователей
users_data = {}

# =================== Проверка пользователя в Google Sheets ===================
def check_user_exists(user_id: int) -> bool:
    """
    Отправляет GET-запрос к Google Apps Script, чтобы проверить,
    есть ли пользователь в таблице.
    """
    try:
        response = requests.get(GOOGLE_SCRIPT_URL, params={"check_user": user_id}, timeout=10)
        data = response.json()
        return data.get("exists", False)
    except Exception as e:
        print("Ошибка проверки пользователя:", e)
        return False

# =================== Команда /start ===================
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_exists = check_user_exists(user_id) or user_id in users_data

    if user_exists:
        # Пользователь уже есть → сразу спрашиваем предложение
        await state.set_state(Form.suggestion)
        await message.answer("Рад снова видеть! Напиши своё новое предложение 👇")
    else:
        # Новый пользователь → собираем ФИО
        await state.set_state(Form.fio)
        await message.answer("Привет! Давай познакомимся 😊\nВведите ваше ФИО:")

# =================== FSM: ФИО ===================
@dp.message(Form.fio)
async def process_fio(message: types.Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await state.set_state(Form.position)
    await message.answer("Введите вашу должность:")

# =================== FSM: Должность ===================
@dp.message(Form.position)
async def process_position(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text)
    await state.set_state(Form.department)
    await message.answer("Введите ваш отдел:")

# =================== FSM: Отдел ===================
@dp.message(Form.department)
async def process_department(message: types.Message, state: FSMContext):
    await state.update_data(department=message.text)
    await state.set_state(Form.suggestion)
    await message.answer("Отлично! Теперь напишите своё предложение:")

# =================== FSM: Предложение ===================
@dp.message(Form.suggestion)
async def process_suggestion(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(suggestion=message.text)
    data = await state.get_data()

    payload = {
        "user_id": user_id,
        "fio": data.get("fio", ""),          # пусто для повторного пользователя
        "position": data.get("position", ""),
        "department": data.get("department", ""),
        "suggestion": data.get("suggestion", "")
    }

    try:
        response = requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=10)
        if response.status_code == 200:
            await message.answer("Ваше предложение успешно отправлено! ✅")
        else:
            await message.answer("Не удалось записать данные. Попробуйте позже ❌")
    except Exception as e:
        await message.answer("Ошибка при отправке данных. Попробуйте позже ❌")
        print("Ошибка:", e)

    # Очищаем состояние после отправки
    await state.clear()

# =================== Запуск бота ===================
if __name__ == "__main__":
    dp.run_polling(bot)

