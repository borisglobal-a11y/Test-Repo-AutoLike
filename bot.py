from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from datetime import datetime, time, timedelta
import asyncio
import os

# Укажите ваши данные
api_id = int(os.environ ["api_id"])
api_hash = os.environ ["api_hash"]

# ID чата и ID пользователя
chat_id = int(os.environ ["chat_id"]) #Поменять после тестов
user_id = int(os.environ ["user_id"]) #Поменять после тестов
app = Client("my_account", api_id=api_id, api_hash=api_hash)

# Время, в которое бот должен работать (8:55 до 9:15)
start_time = time(15, 45) #Поменять после тестов / UTC TIME
end_time = time(18, 30)   #Поменять после тестов / UTC TIME
message_start_time = time(17, 30) #Поменять после тестов / Наше время
message_end_time = time(20, 30)   #Поменять после тестов / Наше время

# Дни недели (с понедельника по пятницу)
allowed_weekdays = {0, 1, 2, 3, 4}

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
                                # Проверяем, что количество реакций больше 12
                                if reaction.count >= 12: #Поменять после тестов
                                    '''if reaction.emoji == "👍":
                                        print(f"{datetime.now().strftime('%Y.%m.%d %H:%M')} - Я уже поставил реакцию на сообщение.")
                                        return "DONE"  # Если я уже поставил реакцию, выходим из функции
                                    else:'''
                                await app.send_reaction(chat_id, message.id, "👍")  # Ставим реакцию
                                print(f"{datetime.now().strftime('%Y.%m.%d %H:%M')} - Сообщение с реакцией найдено, поставлен лайк.")
                                return "DONE"  # Останавливаем проверку до следующего дня
            return None
                              
async def main():
    await app.start()  # Запускаем клиента
    print (is_in_time_range())
    sended_reaction = 0
    while (is_in_time_range() and sended_reaction == 0):
        result = await check_likes_and_respond()  # Запускаем проверку
        if result == "DONE":
            print(f"{datetime.now().strftime('%Y.%m.%d %H:%M')} - Остановка до следующего дня.")
            sended_reaction = 1
        else:
            print(f"{datetime.now().strftime('%Y.%m.%d %H:%M')} - Сообщения нет.")
            await asyncio.sleep(60) #Поменять после тестов
    
    now = datetime.now()
    next_run_time_1 = datetime.combine(now.date(), start_time)
    # Создаем время на следующий день в 8:55
    if now.weekday() == 4:
        next_day = now + timedelta(days=3)
    else:
        next_day = now + timedelta(days=1)
    next_run_time_2 = datetime.combine(next_day.date(), start_time)
    
    # Вычисляем разницу
    if now > next_run_time_1:
        wait_time = (next_run_time_2 - now).total_seconds()
        print(f"Ожидание до {next_run_time_2.strftime('%Y-%m-%d %H:%M')} ({wait_time} секунд).")
    else:
        wait_time = (next_run_time_1 - now).total_seconds()
        print(f"Ожидание до {next_run_time_1.strftime('%Y-%m-%d %H:%M')} ({wait_time} секунд).")
    await asyncio.sleep(wait_time)  #Ждем следующего дня для проверки


if __name__ == "__main__":
    app.run(main())