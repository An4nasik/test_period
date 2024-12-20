import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from decouple import config
from handlers import router
from apscheduler.schedulers.asyncio import AsyncIOScheduler


token = config("BOT_TOKEN")

async def main():
    bot = Bot(token)
    dp = Dispatcher(storage=MemoryStorage())
    await bot.set_my_commands([BotCommand(command="create_meet", description="создать новую конференцию"),
                               BotCommand(command="plane_meet", description="запланировать встречу"),
                               BotCommand(command="shedule", description="получить расписание встреч")])
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), )






if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
