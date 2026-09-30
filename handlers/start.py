from aiogram import Router, types
from aiogram.filters import Command
from database.db import addUser, test
from handlers.auth import ar
from handlers.handlers import hr
from handlers.register import rr

mr = Router()
mr.include_router(ar)
mr.include_router(rr)
mr.include_router(hr)

@mr.message(Command('start'))
async def start(message: types.Message):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='Авторизация', callback_data='auth')],
        [types.InlineKeyboardButton(text='Регистрация', callback_data='register')]
    ])

    user = message.from_user

    if not user:
        return

    username = user.username or 'None'

    await addUser(name=user.full_name, username=username, tg_id=user.id)
    await message.delete()
    await message.answer(text='Next step is...', reply_markup=markup)

@mr.message(Command('ids'))
async def ttest(message: types.Message):
    accs = await test()

    await message.answer(text=f'{accs}')
