import sqlite3
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from data.users import Meet
import asyncio
from aiogram.fsm.context import FSMContext
from meet import sample_create_space, sample_get_conference_record, sample_get_space, end
router = Router()
from data import db_session

con = sqlite3.connect("db/users.db", check_same_thread=False)
cur = con.cursor()
db_session.global_init("db/users.db")


@router.message(Command("start"))
async def start(msg: Message):
    await msg.answer("Привет! Чтобы создать встречу, воспользуйся коандой /create_meet")


@router.message(Command("create_meet"))
async def create_meet(msg: Message):
    rsp = await sample_create_space()
    await msg.answer(f"Ваша ссылка на конференцию - {rsp.meeting_uri} \n название конференции - {rsp.name}")

@router.message(Command("end_meeting"))
async def end_meeting(msg: Message):
    db_sess = db_session.create_session()
    meets = db_sess.query(Meet).filter(Meet.user_id == msg.from_user.id).all()
    keyboard_inline = InlineKeyboardMarkup(inline_keyboard=[])
    for x in meets:
        data = str(x.meeting_name)
        records = await sample_get_space(data)
        if records.active_conference:
            keyboard_inline.inline_keyboard.append([InlineKeyboardButton(text=str(data), callback_data=str(data))])

    await msg.answer("Выберите какую конференцию закончить", reply_markup=keyboard_inline)


@router.callback_query()
async def end_curr_meet(clb: CallbackQuery):
    await end(clb.data)
    await clb.bot.send_message(text=str(clb.data) + " была выключена", chat_id=clb.message.chat.id)