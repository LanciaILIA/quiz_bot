import aiosqlite

# Зададим имя базы данных
DB_NAME = 'quiz_bot.db'


async def create_table():
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Создаем таблицу из трех столбцов: id -  номер вопроса - очки
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER, score INTEGER)''')
        # Сохраняем изменения
        await db.commit()


async def create_quiz_index(user_id, index, count):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, score) VALUES (?, ?, ?)', (user_id, index, count))
        # Сохраняем изменения
        await db.commit()


async def get_quiz_index(user_id): # запрос данных
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index, score FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone() # данные одной строки по id пользователя (кортеж)
            if results is not None:
                return results
            else:
                return 0


async def update_quiz_index(user_id, index, count): # передаем данные для изменения в БД
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, score) VALUES (?, ?, ?)', (user_id, index, count))
        # Сохраняем изменения
        await db.commit()




# Вывод статистики игроков квиза
async def get_quiz_result(): # запрос данных
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:  # Получаем запись для всех пользователей
        async with db.execute('SELECT * FROM quiz_state ORDER BY score') as cursor:
            result = await cursor.fetchall() # получаем все строки БД
            return result

























