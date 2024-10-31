import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from errors import BadRequest
from initialize import BOT_APIKEY
from main import prepare_data

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера с использованием памяти для хранения состояний
storage = MemoryStorage()
bot = Bot(token=BOT_APIKEY)
dp = Dispatcher(storage=storage)


class Form(StatesGroup):
    start_point = State()  # Состояние для начальной точки
    end_point = State()  # Состояние для конечной точки
    forecast_days = State()  # Состояние для хранения количества дней прогноза


# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n"
        "Я бот для получения прогноза погоды. Используйте команды /help для получения списка доступных команд."
    )


# Команда /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "Доступные команды:\n"
        "/start - Приветствие и описание бота\n"
        "/help - Список доступных команд\n"
        "/weather - Получить прогноз погоды по маршруту"
    )


# Команда /weather
@dp.message(Command("weather"))
async def cmd_weather(message: types.Message):
    await message.answer(
        "Введите начальную и конечную точки маршрута в формате: lat,lon (например, 55.7558,37.6173) "
        "и выберите временной интервал прогноза.",
        reply_markup=get_weather_keyboard()
    )


def get_weather_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Прогноз на 3 дня", callback_data="3 дня"),
         InlineKeyboardButton(text="Прогноз на 5 дней", callback_data="5 дней")]],
        row_width=2)
    return keyboard


# Обработка нажатий инлайн-кнопок
@dp.callback_query()
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()

    # Сохраняем количество дней в состоянии
    if callback_query.data == "3 дня":
        await state.update_data(forecast_days=3)
        days_text = "3 дня"
    elif callback_query.data == "5 дней":
        await state.update_data(forecast_days=5)
        days_text = "5 дней"

    await callback_query.message.answer(
        f"Вы выбрали прогноз на {days_text}. Введите начальную точку маршрута (lat,lon).")

    await state.set_state(Form.start_point)  # Устанавливаем состояние ожидания начальной точки


# Обработка ввода начальной точки маршрута
@dp.message(Form.start_point)
async def process_start_point(message: types.Message, state: FSMContext):
    try:
        lat, lon = map(float, message.text.split(","))
        await state.update_data(start_point=(lat, lon))  # Сохраняем начальную точку в состоянии
        await message.answer("Начальная точка принята. Теперь введите конечную точку маршрута (lat,lon).")

        await state.set_state(Form.end_point)  # Устанавливаем состояние ожидания конечной точки
    except ValueError:
        await message.answer(
            "Неверный формат! Пожалуйста, введите координаты в формате: lat,lon (например, 55.7558,37.6173).")


# Обработка ввода конечной точки маршрута
@dp.message(Form.end_point)
async def process_end_point(message: types.Message, state: FSMContext):
    try:
        lat, lon = map(float, message.text.split(","))
        user_data = await state.get_data()  # Получаем сохраненные данные
        start_point = user_data['start_point']  # Извлекаем начальную точку
        forecast_days = user_data['forecast_days']  # Извлекаем количество дней прогноза
        try:
            dates, min_temps, max_temps, humidity, wind_speed, precipitation = prepare_data(forecast_days,
                                                                                        start_point[1], start_point[0])
            answer = 'Точка 1:\n'
            for i in range(forecast_days):
                answer += (f'Дата: {dates[i]}\n Минимальная температура (℃): {min_temps[i]}\n'
                           f'Максимальная температура (℃): {max_temps[i]}\nВлажность: {humidity[i]}\n'
                           f'Скорость ветра (км/ч): {wind_speed[i]}\nВероятность осадков: {precipitation[i]}%\n\n')
            dates, min_temps, max_temps, humidity, wind_speed, precipitation = prepare_data(forecast_days,
                                                                                            lon, lat)
            answer += '--------------------\n\nТочка 2:\n'
            for i in range(forecast_days):
                answer += (f'Дата: {dates[i]}\n Минимальная температура (℃): {min_temps[i]}\n'
                           f'Максимальная температура (℃): {max_temps[i]}\nВлажность: {humidity[i]}\n'
                           f'Скорость ветра (км/ч): {wind_speed[i]}\nВероятность осадков: {precipitation[i]}%\n\n')
            await message.answer(answer)
        except BadRequest:
            await message.answer(f"По этим координатам нельзя получить погоду :(")

        finally:
            await state.clear()
    except ValueError:
        await message.answer(
            "Неверный формат! Пожалуйста, введите координаты в формате: lat,lon (например, 55.7558,37.6173).")


# Основная функция для запуска бота
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
