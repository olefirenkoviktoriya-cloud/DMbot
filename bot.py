import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio

# ---------- Настройки ----------
BOT_TOKEN = "8385165542:AAGnUqMG_NkNl6KFhzjFk4QYQ__BOpKK9CY"
WEBAPP_URL = "https://script.google.com/macros/s/AKfycbwSO-V6Bwv1sb-_LczmIeY4WIaX-dnuIy7YQhbppJnIuYC5To2xh8HHpJ9NPPece2bVug/exec"
# --------------------------------

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ---------- FSM для шагов ----------
class Form(StatesGroup):
    name = State()
    position = State()
    department = State()
    suggestion = State()

# ---------- Функция отправки данных ----------
def send_to_sheet(payload: dict) -> bool:
    try:
        resp = requests.post(WEBAPP_URL, json=payload, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        logging.exception("Ошибка при отправке в Apps Script: %s", e)
        return False

# ---------- Старт ----------
@dp.message(Command(commands=["start"]))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Привет! Давай заполним форму.\nКак тебя зовут?")
    await state.set_state(Form.name)

# ---------- Имя ----------
@dp.message(Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Должность:")
    await state.set_state(Form.position)

# ---------- Должность ----------
@dp.message(Form.position)
async def process_position(message: types.Message, state: FSMContext):
    await state.update_data(position=message.text)
    await message.answer("Отдел:")
    await state.set_state(Form.department)

# ---------- Отдел ----------
@dp.message(Form.department)
async def process_department(message: types.Message, state: FSMContext):
    await state.update_data(department=message.text)
    await message.answer("Предложение:")
    await state.set_state(Form.suggestion)

# ---------- Предложение и отправка ----------
@dp.message(Form.suggestion)
async def process_suggestion(message: types.Message, state: FSMContext):
    await state.update_data(suggestion=message.text)
    data = await state.get_data()
    ok = send_to_sheet(data)
    if ok:
        await message.answer("Данные записаны ✅")
    else:
        await message.answer("Не удалось записать данные. Попробуй позже.")
    await state.clear()

# ---------- Запуск ----------
if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
