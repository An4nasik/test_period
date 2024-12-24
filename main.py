import asyncio
import calendar
import datetime
import logging
import sqlite3
import threading
import time
import pytz
import requests
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from decouple import config

from data import db_session
from data.users import Task
from handlers import router

token = config("BOT_TOKEN")
con = sqlite3.connect("db/users.db", check_same_thread=False)
cur = con.cursor()
db_session.global_init("db/users.db")
bot = Bot(token)
dp = Dispatcher(storage=MemoryStorage())
async def main():


    await bot.set_my_commands([BotCommand(command="create_meet", description="создать новую конференцию"),
                               BotCommand(command="plane_meet", description="запланировать встречу"),
                               BotCommand(command="shedule", description="получить расписание встреч")])
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())



def send(task):
    print(task, "прошла")
    keyboard_inline = InlineKeyboardMarkup(inline_keyboard=[])
    keyboard_inline.inline_keyboard.append(
        [InlineKeyboardButton(text="убрать", callback_data="stop")])
    text = f"<b>Напоминание о конференции!</b>\n<b>{task.meeting_name}</b> \nДата - {task.shedule_date} \nВремя - {task.shedule_time} \nСсылка - {task.meet_url}"
    requests.post(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={int(task.chat_id)}&text={text}&parse_mode=HTML")




def day_to_num(date):
    dct = {
        "понедельник": 0,
        "вторник": 1,
        "среда": 2,
        "четверг": 3,
        "пятница": 4,
        "суббота": 5,
        "воскресенье": 6

    }
    return dct[date]

def reminder():
    while True:
        db_sess = db_session.create_session()
        tasks = list(db_sess.query(Task).all())
        db_sess.close()
        for task in tasks:
            if task.shedule_type == "once":
                if ((datetime.datetime.now(pytz.timezone('Europe/Moscow')) - datetime.timedelta(days=0, minutes=5)).time() <= datetime.datetime.strptime(str(task.shedule_time), "%H:%M:%S").time()
                        <= (datetime.datetime.now(pytz.timezone('Europe/Moscow')) + datetime.timedelta(days=0, minutes=5)).time()):
                    send(task)
                    db_sess = db_session.create_session()
                    db_sess.query(Task).filter(Task.id == task.id).delete()
                    db_sess.commit()
                    db_sess.close()

            elif task.shedule_type == "everyweek" and datetime.datetime.strptime(str(task.shedule_date).replace("-", "/"),
                                                        "%Y/%m/%d").date() == datetime.datetime.today().date():
                if ((datetime.datetime.now(pytz.timezone('Europe/Moscow')) - datetime.timedelta(days=0,
                                                               minutes=5)).time() <= datetime.datetime.strptime(
                    str(task.shedule_time), "%H:%M:%S").time()
                 <= (datetime.datetime.now(pytz.timezone('Europe/Moscow')) + datetime.timedelta(days=0, minutes=5)).time()):
                    send(task)
                    db_sess = db_session.create_session()
                    db_sess.query(Task).filter(Task.id == task.id).update({Task.shedule_date: datetime.datetime.strptime(str(task.shedule_date).replace("-", "/"),
                                                        "%Y/%m/%d").date() + datetime.timedelta(7)})
                    db_sess.commit()
                    db_sess.close()
            elif task.shedule_type == "everyday":
                if datetime.datetime.strptime(str(task.shedule_date).replace("-", "/"),
                                                                       "%Y/%m/%d").date() == datetime.datetime.today().date():
                    if ((datetime.datetime.now(pytz.timezone('Europe/Moscow')) - datetime.timedelta(days=0,
                                                                      minutes=5)).time() <= datetime.datetime.strptime(
                            str(task.shedule_time), "%H:%M:%S").time()
                            <= (datetime.datetime.now(pytz.timezone('Europe/Moscow')) + datetime.timedelta(days=0, minutes=5)).time()):
                        send(task)
                        db_sess = db_session.create_session()
                        db_sess.query(Task).filter(Task.id == task.id).update(
                            {Task.shedule_date: datetime.datetime.strptime(str(task.shedule_date).replace("-", "/"),
                                                                           "%Y/%m/%d").date() + datetime.timedelta(1)})
                        db_sess.commit()
                        db_sess.close()
            elif task.shedule_type == "everymonth":
                if datetime.datetime.strptime(str(task.shedule_date).replace("-", "/"),
                                                                       "%Y/%m/%d").date() == datetime.datetime.today().date():
                    if ((datetime.datetime.now() - datetime.timedelta(days=0,
                                                                      minutes=5)).time() <= datetime.datetime.strptime(
                        str(task.shedule_time), "%H:%M:%S").time()
                            <= (datetime.datetime.now() + datetime.timedelta(days=0, minutes=5)).time()):
                        send(task)
                        db_sess = db_session.create_session()
                        date = datetime.datetime.today().date()
                        days_in_month = calendar.monthrange(date.year, date.month)[1]
                        db_sess.query(Task).filter(Task.id == task.id).update(
                            {Task.shedule_date: datetime.datetime.strptime(str(task.shedule_date).replace("-", "/"),
                                                                           "%Y/%m/%d").date() + datetime.timedelta(days=days_in_month)})
                        db_sess.commit()
                        db_sess.close()
        time.sleep(20)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    thread = threading.Thread(target=reminder)
    thread.start()
    asyncio.run(main())
