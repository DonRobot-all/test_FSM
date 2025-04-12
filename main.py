import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# Загрузка токена из .env
load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")

# FSM состояния
class Form(StatesGroup):
    gender = State()
    name = State()

# Клавиатура выбора пола
gender_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👦 Мальчик")],
        [KeyboardButton(text="👧 Девочка")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# /start
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Привет! Кто ты?", reply_markup=gender_kb)
    await state.set_state(Form.gender)

# Обработка пола
async def gender_chosen(message: Message, state: FSMContext):
    if message.text not in ["👦 Мальчик", "👧 Девочка"]:
        return await message.answer("Пожалуйста, выбери вариант с клавиатуры.")
    await state.update_data(gender=message.text)
    await message.answer("Как тебя зовут?", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Form.name)

# Обработка имени
async def name_chosen(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    await message.answer(
        f"Приятно познакомиться, <b>{data['name']}</b>!\n"
        f"Ты выбрал: {data['gender'].lower()} 😎",
        parse_mode=ParseMode.HTML
    )
    await state.clear()

# /cancel
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Окей, всё сбросил. Напиши /start, чтобы начать заново.", reply_markup=ReplyKeyboardRemove())

# Запуск бота
async def main():
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.message.register(cmd_start, F.text == "/start")
    dp.message.register(cancel_handler, F.text == "/cancel")
    dp.message.register(gender_chosen, Form.gender)
    dp.message.register(name_chosen, Form.name)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
