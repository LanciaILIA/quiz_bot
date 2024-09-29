# import aiosqlite
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F
from config import TOKEN
from question import quiz_data
from bd import *

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Объект бота
bot = Bot(token=TOKEN)
# Диспетчер
dp = Dispatcher()


def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    builder.adjust(1)
    return builder.as_markup()


@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    await callback.message.answer("Верно!")
    current_question_index = await get_quiz_index(callback.from_user.id)
    # Обновление номера текущего вопроса в базе данных для конкретного пользователя (user.id)
    index = current_question_index[0] # выбор из переданного кортежа данных первого столбца
    index += 1
    score = current_question_index[1] # выбор из переданного кортежа данных второго столбца
    score += 1
    await update_quiz_index(callback.from_user.id, index, score) # отправка измененных данных

    if index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")
        await asyncio.sleep(1)
        await callback.message.answer("Рейтинг игроков: id - вопросв - верные ответы")
        rating = await get_quiz_result() # получение данных
        results = '/n'.join([str(res) for res in rating]) # сбор и перевод в строку данных из кортежа от БД
        await callback.message.answer(results) # вывод результата



@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)
    index = current_question_index[0]
    correct_option = quiz_data[index]['correct_option']
    current_count = await get_quiz_index(callback.from_user.id)

    await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[index]['options'][correct_option]}")
    # Обновление номера текущего вопроса в базе данных
    index += 1
    score = current_question_index[1]
    score += 0
    await update_quiz_index(callback.from_user.id, index, score)

    if index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")
        await asyncio.sleep(1)
        await callback.message.answer("Рейтинг игроков: id - вопросы - верные ответы")
        rating = await get_quiz_result()
        results = '/n'.join([str(res) for res in rating])
        await callback.message.answer(results)


# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))


async def get_question(message, user_id):

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    index = current_question_index[0]
    correct_index = quiz_data[index]['correct_option']
    opts = quiz_data[index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[index]['question']}", reply_markup=kb)


async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    current_count = 0
    await create_quiz_index(user_id, current_question_index, current_count)
    await get_question(message, user_id)


# Хэндлер на команду /quiz
@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)



# Запуск процесса поллинга новых апдейтов
async def main():

    # Запускаем создание таблицы базы данных
    await create_table()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())