from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from datetime import datetime, time, timedelta
import logging
import logging.handlers
import asyncio
import os
import sys

# Укажите ваши данные
api_id = int(os.environ ["api_id"])
api_hash = os.environ ["api_hash"]

# ID чата и ID пользователя
chat_id = int(os.environ ["chat_id"]) #Поменять после тестов
user_id = int(os.environ ["user_id"]) #Поменять после тестов

# Время, в которое бот должен работать (8:40 до 9:30)
start_time = time(6, 55) #Поменять после тестов / Установить UTC TIME для Github Actions
end_time = time(7, 30)   #Поменять после тестов / Установить UTC TIME для Github Actions
message_start_time = time(6, 20) #Поменять после тестов / Установить UTC TIME для Github Actions
message_end_time = time(7, 30)   #Поменять после тестов / Установить UTC TIME для Github Actions

# Дни недели (с понедельника по пятницу)
allowed_weekdays = {0, 1, 2, 3, 4}

#Добавляем логи
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "status.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)

app = Client("my_account", api_id=api_id, api_hash=api_hash)

# Проверка, находится ли текущее время в нужном диапазоне
def is_in_time_range():
    now = datetime.now().time()
    today = datetime.now().weekday()
    return start_time <= now <= end_time and today in allowed_weekdays

# Проверка, было ли сообщение отправлено в нужный временной диапазон
def is_message_today_and_in_time_range(message_time):
    now = datetime.now()
    return message_time.date() == now.date() and message_start_time <= message_time.time() <= message_end_time

# Обработчик сообщений
async def check_likes_and_respond():
        if is_in_time_range():
            async for message in app.get_chat_history(chat_id, limit=100):
                # Проверяем сообщения от нужного пользователя
                if message.from_user and message.from_user.id == user_id:
                    if is_message_today_and_in_time_range(message.date):
                        reactions = message.reactions
                        if reactions:
                            for reaction in reactions.reactions:
                                # Проверяем, что количество реакций больше 15
                                if reaction.count >= 15: #Поменять после тестов
                                    '''if reaction.emoji == "👍":
                                        print(f"{datetime.now().strftime('%Y.%m.%d %H:%M')} - Я уже поставил реакцию на сообщение.")
                                        return "DONE"  # Если я уже поставил реакцию, выходим из функции
                                    else:'''
                                await app.send_reaction(chat_id, message.id, "👍")  # Ставим реакцию
                                print(f"{datetime.now().strftime('%Y.%m.%d %H:%M')} - Сообщение с реакцией найдено, поставлен лайк.")
                                logger.info(f'(UTC Time) | Сообщение с реакцией найдено, поставлен лайк.')
                                return "DONE"  # Останавливаем проверку до следующего дня
            return None
                              
async def main():
    await app.start()  # Запускаем клиента
    if is_in_time_range() == 0:
        logger.info(f'(UTC Time) | Еще не наступило время для работы.')
    else:
        logger.info(f'(UTC Time) | Время наступило.')
    sended_reaction = 0
    while (is_in_time_range() and sended_reaction == 0):
        result = await check_likes_and_respond()  # Запускаем проверку
        if result == "DONE":
            print(f"{datetime.now().strftime('%Y.%m.%d %H:%M')} - Остановка до следующего дня.")
            logger.info(f'(UTC Time) | Остановка до следующего дня.')
            sended_reaction = 1
        else:
            print(f"{datetime.now().strftime('%Y.%m.%d %H:%M')} - Сообщения нет.")
            logger.info(f'(UTC Time) | Сообщения нет.')
            await asyncio.sleep(60) #Поменять после тестов
    
    now = datetime.now()

    if now.weekday() == 4:
        next_day = now + timedelta(days=3)
    else:
        if now.weekday() == 5:
            next_day = now + timedelta(days=2)
        else:
            if now.weekday() == 6:
                next_day = now + timedelta(days=1)
            else:
                next_day = now + timedelta(days=0)

    next_run_time_1 = datetime.combine(next_day.date(), start_time)

    if now.weekday() == 4:
        next_day = now + timedelta(days=3)
    else:
        if now.weekday() == 5:
            next_day = now + timedelta(days=2)
        else:
            next_day = now + timedelta(days=1)
            
    next_run_time_2 = datetime.combine(next_day.date(), start_time)
    
    # Вычисляем разницу
    if now > next_run_time_1:
        wait_time = (next_run_time_2 - now).total_seconds()
        print(f"Ожидание до {next_run_time_2.strftime('%Y-%m-%d %H:%M')} ({wait_time} секунд).")
        logger.info(f'(UTC Time) | Ожидание до {next_run_time_2.strftime("%Y-%m-%d %H:%M")} ({wait_time} секунд).')
    else:
        wait_time = (next_run_time_1 - now).total_seconds()
        print(f"Ожидание до {next_run_time_1.strftime('%Y-%m-%d %H:%M')} ({wait_time} секунд).")
        logger.info(f'(UTC Time) | Ожидание до {next_run_time_1.strftime("%Y-%m-%d %H:%M")} ({wait_time} секунд).')
    sys.exit(0)
    #await asyncio.sleep(wait_time)  #Ждем следующего дня для проверки


if __name__ == "__main__":
    app.run(main())