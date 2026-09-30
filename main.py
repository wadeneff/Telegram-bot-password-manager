import asyncio

from aiogram import Bot, Dispatcher
from config import api
from database.db import init_db
from handlers.start import mr

bot = Bot(api)
dp = Dispatcher()
dp.include_router(mr)

async def main():
    await init_db()

    print(f'\n\n{'-'*8}{'='*5} THE BOT WAS SUCCEFULLY STARTED {'='*5}{'-'*8}\n\n')

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
