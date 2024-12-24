import sqlite3
from datetime import datetime
import datetime as dtm
from datetime import time
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from aiogram_calendar import get_user_locale
from data.users import Task
from meet import sample_create_space


router = Router()
from data import db_session

con = sqlite3.connect("db/users.db", check_same_thread=False)
cur = con.cursor()
db_session.global_init("db/users.db")



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

class Form(StatesGroup):
    data = State()
    name = State()
    final = State()
    # db_sess = db_session.create_session()
    # shedules = db_sess.query(Task).filter(Task.user_id == msg.from_user.id).all()


async def get_frequency_of_meetings(data: str) -> str:
    ans = ""
    if "day" in data:
        ans = "Каждый день"
    elif "week" in data:
        ans = "Каждую неделю"
    elif "month" in data:
        ans = "Каждый месяц"
    return ans


@router.message(Command("shedule"))
async def get_shedule(msg: Message):
    keyboard_inline = InlineKeyboardMarkup(inline_keyboard=[])
    keyboard_inline.inline_keyboard.append([InlineKeyboardButton(text="Регулярные", callback_data="every 0"),
                                            InlineKeyboardButton(text="Разовые", callback_data="once 0")])
    await msg.answer("Выберите тип встреч, расписание которых желаете получить", reply_markup=keyboard_inline)


@router.message(Command("start"))
async def start(msg: Message):
    await msg.answer("Привет! Чтобы создать встречу, воспользуйся командой /create_meet ",
                     reply_markup=types.ReplyKeyboardRemove())


@router.message(Command("create_meet"))
async def create_meet(msg: Message):
    rsp = await sample_create_space()
    await msg.answer(f"Ваша ссылка на конференцию - {rsp.meeting_uri} \n название конференции - {rsp.name}")



# @router.message(Command("end_meeting"))
# async def end_meeting(msg: Message):
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
        db_sess = db_session.create_session()
        print(clq.data)
        meets = list(
            db_sess.query(Task).filter(Task.shedule_type.ilike("every%") & (Task.chat_id == clq.message.chat.id)).slice(
                start=int(data.split()[-1]), stop=int(data.split()[-1]) + 5))
        db_sess.close()
        if meets:
            ans = ""
            for meet in meets:
                ans = ans + (
                    f"\n"
                    f"<b>{meet.meeting_name} </b>"
                    f"\n"
                    f"Время - {str(meet.shedule_time)[:-3]} \n"
                    f"Дата - {meet.shedule_date} \n"
                    f"Частота повторений - {await get_frequency_of_meetings(str(meet.shedule_type))} \n"
                    f"Ссылка на встречу - {meet.meet_url} \n"
                    f"Удалить конференцию - /delete{meet.id}"
                    f"\n")
            keyboard_inline = InlineKeyboardMarkup(inline_keyboard=[])
            keyboard_inline.inline_keyboard.append(
                [InlineKeyboardButton(text="⬅", callback_data=("every " + str(int(data.split()[-1]) - 5))),
                 InlineKeyboardButton(text="➡", callback_data=("every " + str(int(data.split()[-1]) + 5)))])
            keyboard_inline.inline_keyboard.append(
                [InlineKeyboardButton(text="убрать", callback_data="stop")])
            await clq.bot.edit_message_text(ans,
                                            chat_id=clq.message.chat.id,
                                            message_id=clq.message.message_id,
                                            reply_markup=keyboard_inline,
                                            parse_mode="HTML")


@router.callback_query(F.data.split()[0] == "once")
async def get_once_meets(clq: CallbackQuery):
    await clq.answer()
    data = clq.data
    if int(data.split()[-1]) < 0:
        data = str(clq.data.split()[0]) + " 5"
    else:
        db_sess = db_session.create_session()
        meets = list(
            db_sess.query(Task).filter(Task.shedule_type.ilike("once%") & (Task.chat_id == clq.message.chat.id)).slice(
                start=int(data.split()[-1]), stop=int(data.split()[-1]) + 5))
        db_sess.close()
        if meets:
            ans = ""
            for meet in meets:
                ans = ans + (
                    f"\n"
                    f"<b>{meet.meeting_name} </b>"
                    f"\n"
                    f"Время - {str(meet.shedule_time)[:-3]} \n"
                    f"Дата - {meet.shedule_date} \n"
                    f"Частота повторений - {await get_frequency_of_meetings(str(meet.shedule_type))} \n"
                    f"Ссылка на встречу - {meet.meet_url}\n"
                    f"Удалить конференцию - /delete{meet.id}"
                    f"\n")
            keyboard_inline = InlineKeyboardMarkup(inline_keyboard=[])
            keyboard_inline.inline_keyboard.append(
                [InlineKeyboardButton(text="⬅", callback_data=("once " + str(int(data.split()[-1]) - 5))),
                 InlineKeyboardButton(text="➡", callback_data=("once " + str(int(data.split()[-1]) + 5)))])
            keyboard_inline.inline_keyboard.append(
                [InlineKeyboardButton(text="убрать", callback_data="stop")])
            await clq.bot.edit_message_text(ans,
                                            chat_id=clq.message.chat.id,
                                            message_id=clq.message.message_id,
                                            reply_markup=keyboard_inline,
                                            parse_mode="HTML")



@router.message(Form.name)
async def setting_name(msg: Message, state: FSMContext):
    task = await state.get_value("task")
    task.meeting_name = msg.text
    tsk = Task(
        user_id=task.user_id,
        meeting_name=task.meeting_name,
        meet_url=task.meet_url,
        meeting_code=task.meeting_code,
        shedule_time=str(task.shedule_time),
        shedule_date=task.shedule_date,
        shedule_type=task.shedule_type,
        chat_id=msg.chat.id

    )
    db_sess = db_session.create_session()
    msg_id = await state.get_value("msg_id")
    for x in msg_id[1:]:
        await msg.bot.delete_message(chat_id=msg.chat.id, message_id=x)
    keyboard_inline = InlineKeyboardMarkup(inline_keyboard=[])
    keyboard_inline.inline_keyboard.append(
        [InlineKeyboardButton(text="убрать", callback_data="stop")])
    await msg.bot.edit_message_text(f"Встреча успешо добавлена \n"
                                    f"<b>{tsk.meeting_name}\n </b>"
                                    f"\n"
                                    f"Время - {str(task.shedule_time)[:-3]} \n"
                                    f"Дата - {tsk.shedule_date} \n"
                                    f"Ссылка - {task.meet_url}", parse_mode="HTML", message_id=msg_id[0],
                                    chat_id=msg.chat.id,
                                    reply_markup=keyboard_inline)
    db_sess.add(tsk)
    db_sess.commit()
    db_sess.close()
    await state.clear()


@router.message(Command("plane_meet"))
async def nav_cal_handler(message: Message, state: FSMContext):
    keyboard_inline = InlineKeyboardMarkup(inline_keyboard=[])
    keyboard_inline.inline_keyboard.append(
        [InlineKeyboardButton(text="Одноразовая", callback_data="repeat once Одноразовая"),
         InlineKeyboardButton(text="Каждый день", callback_data="repeat everyday Каждый день")])
    keyboard_inline.inline_keyboard.append(
        [InlineKeyboardButton(text="Раз в неделю", callback_data="repeat everyweek Раз в неделю"),
         InlineKeyboardButton(text="Каждый месяц", callback_data="repeat everymonth Каждый месяц")])
    keyboard_inline.inline_keyboard.append([InlineKeyboardButton(text="Отмена", callback_data="stop")])
    await message.answer("Выберите количество повторений встречи: ", reply_markup=keyboard_inline)


@router.callback_query(F.data.split()[1] == "everyday")
async def everyday_meeting_plane(clq: CallbackQuery, state: FSMContext):
    await clq.answer(show_alert=False)
    tsk = Task(shedule_type="everyday")
    await state.set_data({"task": tsk})
    msg = await clq.bot.edit_message_text(
        f'Пожалуйста напишите время встречи в формате hh:mm \n'
        f'Например 11:20', chat_id=clq.message.chat.id,
        message_id=clq.message.message_id
    )
    await state.update_data({"msg_id": [msg.message_id]})
    msg = clq.message
    meet = await sample_create_space()
    st = await state.get_value("task")
    task = Task(
        shedule_type=st.shedule_type,
        user_id=msg.from_user.id,
        meet_url=meet.meeting_uri,
        meeting_code=meet.meeting_code,
        meeting_name=meet.name,
        shedule_date=str(dtm.datetime.today().date())

    )
    await state.update_data({"task": task})
    await state.set_state(Form.data)


@router.callback_query(F.data.split()[1] == "everyweek")
async def everyweek_meeting_plane(clq: CallbackQuery, state: FSMContext):
    await clq.answer(show_alert=False)
    tsk = Task(shedule_type="everyweek")
    await state.set_data({"task": tsk})
    keyboard_inline = InlineKeyboardMarkup(inline_keyboard=[])
    keyboard_inline.inline_keyboard.append(
        [InlineKeyboardButton(text="Понедельник", callback_data="week понедельник"),
         InlineKeyboardButton(text="Вторник", callback_data="week вторник"),
         InlineKeyboardButton(text="Среда", callback_data="week среда"),
         InlineKeyboardButton(text="Четверг", callback_data="week четверг"),
         InlineKeyboardButton(text="Пятница", callback_data="week пятница"),
         InlineKeyboardButton(text="Суббота", callback_data="week суббота"),
         InlineKeyboardButton(text="Воскресенье", callback_data="week воскресенье")])
    await clq.bot.edit_message_text("Пожалуйста выберите день недели", reply_markup=keyboard_inline,
                                    chat_id=clq.message.chat.id,
                                    message_id=clq.message.message_id)


@router.callback_query(F.data.split()[0] == "week")
async def weekly_meeting_time(clq: CallbackQuery, state: FSMContext):
    await clq.answer(show_alert=False)
    tsk = await state.get_value("task")
    msg = await clq.bot.edit_message_text(
        f'Пожалуйста напишите время встречи в формате hh:mm \n'
        f'Например 11:20', chat_id=clq.message.chat.id,
        message_id=clq.message.message_id
    )
    await state.update_data({"msg_id": [msg.message_id]})
    msg = clq.message
    meet = await sample_create_space()
    st = await state.get_value("task")
    date = dtm.datetime.today().weekday()
    ans = ""
    if date > day_to_num(clq.data.split()[-1]):
        ans = dtm.datetime.today().date() +  dtm.timedelta(dtm.datetime.today().date().weekday() - day_to_num(clq.data.split()[-1]))
    else:
        ans = dtm.datetime.today().date()+ dtm.timedelta(day_to_num(clq.data.split()[-1]) - dtm.datetime.today().date().weekday())
    task = Task(
        shedule_type=st.shedule_type,
        user_id=msg.from_user.id,
        meet_url=meet.meeting_uri,
        meeting_code=meet.meeting_code,
        meeting_name=meet.name,
        shedule_date=str(ans)

    )
    await state.update_data({"task": task})
    await state.set_state(Form.data)


@router.callback_query(F.data.split()[1] == "once")
async def one_meeting_plane(clq: CallbackQuery, state: FSMContext):
    await clq.answer(show_alert=False)
    tsk = Task(
        shedule_type="once"
    )
    await state.set_data({"task": tsk})
    await clq.bot.edit_message_text(
        "Пожалуйста выберите дату: ",
        reply_markup=await SimpleCalendar(locale="RU").start_calendar(),
        message_id=clq.message.message_id,
        chat_id=clq.message.chat.id
    )


@router.callback_query(F.data.split()[1] == "everymonth")
async def one_meeting_plane(clq: CallbackQuery, state: FSMContext):
    await clq.answer(show_alert=False)
    tsk = Task(
        shedule_type="everymonth"
    )
    await state.set_data({"task": tsk})
    await clq.bot.edit_message_text(
        "Пожалуйста выберите дату: ",
        reply_markup=await SimpleCalendar(locale="RU").start_calendar(),
        message_id=clq.message.message_id,
        chat_id=clq.message.chat.id
    )


@router.callback_query(SimpleCalendarCallback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = SimpleCalendar(
        locale=await get_user_locale(callback_query.from_user), show_alerts=True
    )
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    if selected:
        if date.date() >= dtm.date.today():
            msg = await callback_query.bot.edit_message_text(
                f'Вы выбрали {date.strftime("%d/%m/%Y")} \n'
                f'Пожалуйста напишите время встречи в формате hh:mm \n'
                f'Например 11:20', chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                reply_markup=None
            )
            await state.update_data({"msg_id": [msg.message_id]})
            msg = callback_query.message
            meet = await sample_create_space()
            st = await state.get_value("task")
            task = Task(
                shedule_type=st.shedule_type,
                user_id=msg.from_user.id,
                meet_url=meet.meeting_uri,
                meeting_code=meet.meeting_code,
                meeting_name=meet.name,
                shedule_date=date.strftime("%Y/%m/%d")

            )
            await state.update_data({"task": task})
            await state.set_state(Form.data)
        else:
            await callback_query.bot.edit_message_text(
                "Нельзя выбрать прошедший день \n"
                "Пожалуйста выберите дату: ",
                reply_markup=await SimpleCalendar(locale="RU").start_calendar(),
                message_id=callback_query.message.message_id,
                chat_id=callback_query.message.chat.id
            )


@router.message(Form.data)
async def adding_meet(msg: Message, state: FSMContext):
    try:
        a = time.fromisoformat(msg.text)
    except Exception:
        m = await msg.answer("Неправильный формат, попробуйте еще раз")
        a = await state.get_value("msg_id")
        a.append(m.message_id)
        await state.update_data({"msg_id": a})
    else:
        task = await state.get_value("task")
        task.shedule_time = a
        msg_id = await state.get_value("msg_id")
        await state.clear()
        for x in msg_id[1:]:
            await msg.bot.delete_message(msg.chat.id, x)
        await msg.bot.edit_message_text("Напишите название конференции",
                                        chat_id=msg.chat.id,
                                        message_id=msg_id[0])
        await state.set_data({"task": task, "msg_id": [msg_id[0]]})
        await state.set_state(Form.name)


@router.callback_query(F.data.split()[0] == "stop")
async def stop(clq: CallbackQuery):
    await clq.message.delete()


@router.callback_query()
def foo(clq: CallbackQuery):
    print(clq.data)


@router.message(F.text.split("@")[0][:7] == "/delete")
async def delete_meet(msg: Message):
    db_sess = db_session.create_session()
    print(db_sess.query(Task).filter(Task.id == int(msg.text.split("@")[0][7:])).delete())
    db_sess.commit()
    db_sess.close()
    
