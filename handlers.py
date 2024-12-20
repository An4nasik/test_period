import sqlite3
from datetime import datetime
from datetime import time
from aiogram.fsm.context import FSMContext
from aiogram import Router, F, types
from aiogram.filters import Filter
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, DialogCalendar
from aiogram_calendar import get_user_locale
from sqlalchemy.orm import defer

from data.users import Task
from meet import sample_create_space, sample_get_space

router = Router()
from data import db_session

con = sqlite3.connect("db/users.db", check_same_thread=False)
cur = con.cursor()
db_session.global_init("db/users.db")

class Form(StatesGroup):
    data = State()

    #db_sess = db_session.create_session()
    #shedules = db_sess.query(Task).filter(Task.user_id == msg.from_user.id).all()


async def get_frequency_of_meetings(data: str) -> str:
    ans = ""
    if "day" in data:
        ans = "Каждый день"
    elif "week" in data:
        ans = "Каждую неделю"
    elif "month" in data:
        ans = "Каждый месяц"
    return  ans


@router.message(Command("shedule"))
async  def get_shedule(msg: Message):
    keyboard_inline = InlineKeyboardMarkup(inline_keyboard=[])
    keyboard_inline.inline_keyboard .append([InlineKeyboardButton(text="Регулярные", callback_data="every 0"),
                                             InlineKeyboardButton(text="Разовые", callback_data="once 0")])
    await msg.answer("Выберите тип встреч, расписание которых желаете получить", reply_markup=keyboard_inline)


@router.message(Command("start"))
async def start(msg: Message):
    await msg.answer("Привет! Чтобы создать встречу, воспользуйся командой /create_meet", reply_markup =types.ReplyKeyboardRemove())


@router.message(Command("create_meet"))
async def create_meet(msg: Message):
    rsp = await sample_create_space()
    await msg.answer(f"Ваша ссылка на конференцию - {rsp.meeting_uri} \n название конференции - {rsp.name}")

#@router.message(Command("end_meeting"))
#async def end_meeting(msg: Message):
#    db_sess = db_session.create_session()
#    meets = db_sess.query(Task).filter(Task.user_id == msg.from_user.id).all()
#    keyboard_inline = InlineKeyboardMarkup(inline_keyboard=[])
#    for x in meets:
#        data = str(x.meeting_name)
#        records = await sample_get_space(data)
#        if records.active_conference:
#            keyboard_inline.inline_keyboard.append([InlineKeyboardButton(text=str(data), callback_data=str(data))])
#
#    await msg.answer("Выберите какую конференцию закончить", reply_markup=keyboard_inline)

@router.callback_query(F.data.split()[0] == "every")
async def get_every_meets(clq: CallbackQuery):
    await clq.answer()
    data = clq.data
    if int(data.split()[-1]) < 0:
        data = str(clq.data.split()[0]) + " 5"
    else:
        keyboard_inline = InlineKeyboardMarkup(inline_keyboard=[])
        keyboard_inline.inline_keyboard.append([InlineKeyboardButton(text="⬅", callback_data=("every " + str(int(data.split()[-1]) - 5))),
                                                InlineKeyboardButton(text="➡", callback_data=("every " + str(int(data.split()[-1]) + 5)))])
        db_sess = db_session.create_session()
        print(clq.data)
        meets = list(db_sess.query(Task).filter(Task.shedule_type.ilike("every%")).slice(start=int(data.split()[-1]), stop=int(data.split()[-1]) + 5))
        db_sess.close()
        if meets:
            for meet in meets[int(data[-1]): len(meets) - 1]:
                await clq.message.answer(f"Время - {meet.shedule_time} \n"
                                         f"Дата - {meet.shedule_date} \n"
                                         f"Частота повторений - {await get_frequency_of_meetings(str(meet.shedule_type))} \n"
                                         f"Ссылка на встречу - {meet.meet_url}", reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(text="Удалить", callback_data=("delete " + str(meet.id)))]]))
            meet = meets[-1]
            keyboard_inline.inline_keyboard.insert(0, [
                InlineKeyboardButton(text="Удалить", callback_data=("delete " + str(meet.id)))])
            await clq.message.answer(f"Время - {meet.shedule_time} \n"
                                     f"Дата - {meet.shedule_date} \n"
                                     f"Частота повторений - {await get_frequency_of_meetings(str(meet.shedule_type))} \n"
                                     f"Ссылка на встречу - {meet.meet_url}", reply_markup=keyboard_inline)
        else:
            keyboard_inline = InlineKeyboardMarkup(inline_keyboard=[])
            keyboard_inline.inline_keyboard.append(
                [InlineKeyboardButton(text="⬅", callback_data=("every " + str(int(data.split()[-1]) - 5)))])
            await clq.message.answer(f"Конец списка конференций", reply_markup=keyboard_inline)



@router.callback_query(F.data.split()[0] == "once")
async def get_once_meets(clq: CallbackQuery):
    await clq.answer()
    data = clq.data
    if int(data.split()[-1]) < 0:
        data = str(clq.data.split()[0]) + " 5"
    else:
        keyboard_inline = InlineKeyboardMarkup(inline_keyboard=[])
        keyboard_inline.inline_keyboard.append([InlineKeyboardButton(text="⬅", callback_data=("once " + str(int(data.split()[-1]) - 5))),
                                                InlineKeyboardButton(text="➡", callback_data=("once " + str(int(data.split()[-1]) + 5)))])
        db_sess = db_session.create_session()
        print(clq.data)
        meets = list(db_sess.query(Task).filter(Task.shedule_type.ilike("once%")).slice(start=int(data.split()[-1]), stop=int(data.split()[-1]) + 5))
        db_sess.close()
        if meets:
            for meet in meets[int(data[-1]): len(meets) - 1]:
                await clq.message.answer(f"Время - {meet.shedule_time} \n"
                                         f"Дата - {meet.shedule_date} \n"
                                         f"Ссылка на встречу - {meet.meet_url}", reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(text="Удалить", callback_data=("delete " + str(meet.id)))]]))
            meet = meets[-1]
            keyboard_inline.inline_keyboard.insert(0, [
                InlineKeyboardButton(text="Удалить", callback_data=("delete " + str(meet.id)))])
            await clq.message.answer(f"Время - {meet.shedule_time} \n"
                                     f"Дата - {meet.shedule_date} \n"
                                     f"Ссылка на встречу - {meet.meet_url}", reply_markup=keyboard_inline)
        else:
            keyboard_inline = InlineKeyboardMarkup(inline_keyboard=[])
            keyboard_inline.inline_keyboard.append(
                [InlineKeyboardButton(text="⬅", callback_data=("once " + str(int(data.split()[-1]) - 5)))])
            await clq.message.answer(f"Конец списка конференций", reply_markup=keyboard_inline)





@router.callback_query(F.data.split()[0] == "delete")
async def delete_meet(clq: CallbackQuery):
    await clq.answer()
    db_sess = db_session.create_session()
    db_sess.query(Task).filter(Task.id == int(clq.data.split()[-1])).delete()
    db_sess.commit()
    db_sess.close()
    await clq.message.delete()


@router.callback_query(F.data.split()[0] == "repeat")
async def add_new_meet(clq: CallbackQuery, state: FSMContext, ):
    await clq.answer(show_alert=False)
    task = await state.get_value("task")
    task.shedule_type = clq.data.split()[1]
    tsk = Task(
        user_id=task.user_id,
        meeting_name=task.meeting_name,
        meet_url=task.meet_url,
        meeting_code=task.meeting_code,
        shedule_time=str(task.shedule_time),
        shedule_date=task.shedule_date,
        shedule_type=task.shedule_type,
        chat_id=clq.message.chat.id

    )
    db_sess = db_session.create_session()

    await clq.message.answer(f"Встреча успешо добавлена \n"
                             f"Время - {str(task.shedule_time)} \n"
                             f"Дата - {tsk.shedule_date} \n"
                             f"Ссылка - {task.meet_url}")
    db_sess.add(tsk)
    db_sess.commit()
    db_sess.close()


@router.message(Command("plane_meet"))
async def nav_cal_handler(message: Message, state: FSMContext):
    await message.answer(
        "Пожалуйста выберите дату: ",
        reply_markup=await SimpleCalendar(locale="RU").start_calendar()
    )



@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):

    calendar = SimpleCalendar(
        locale=await get_user_locale(callback_query.from_user), show_alerts=True
    )
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.delete()
        msg = callback_query.message
        meet = await sample_create_space()
        task = Task(
            user_id=msg.from_user.id,
            meet_url=meet.meeting_uri,
            meeting_code=meet.meeting_code,
            meeting_name=meet.name,
            shedule_date=date.strftime("%d/%m/%Y")

        )
        await state.set_data({"task": task})
        await state.set_state(Form.data)
        await callback_query.message.answer(
            f'Вы выбрали {date.strftime("%d/%m/%Y")} \n'
            f'Пожалуйста напишите время встречи в формате hh:mm \n'
            f'Например 11:20',
        )

@router.message(Form.data)
async def adding_meet(msg: Message, state: FSMContext):
    try:
        a = time.fromisoformat(msg.text)
    except Exception:
        await msg.answer("Неправильный формат, попробуйте еще раз")
    else:
        keyboard_inline = InlineKeyboardMarkup(inline_keyboard=[])
        keyboard_inline.inline_keyboard.append([InlineKeyboardButton(text="Одноразовая", callback_data="repeat once Одноразовая"),
                                                InlineKeyboardButton(text="Каждый день", callback_data="repeat everyday Каждый день")])
        keyboard_inline.inline_keyboard.append([InlineKeyboardButton(text="Раз в неделю", callback_data="repeat everyweek Раз в неделю"),
                                                InlineKeyboardButton(text="Каждый месяц", callback_data="repeat everymonth Каждый месяц")])
        keyboard_inline.inline_keyboard.append([InlineKeyboardButton(text="Отмена", callback_data="stop")])
        task = await state.get_value("task")
        task.shedule_time = a
        await state.clear()
        await state.set_data({"task": task})
        await msg.answer("Выбрите количество повторений встречи: ", reply_markup=keyboard_inline)


@router.callback_query()
def foo(clq: CallbackQuery):
    print(clq.data)