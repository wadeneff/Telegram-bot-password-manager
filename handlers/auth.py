from aiogram import Bot, F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import authing
from handlers.register import userAccState

ar = Router()

class authStates(StatesGroup):
    login = State()
    password = State()

@ar.callback_query(F.data == 'auth')
async def auth(callback: types.CallbackQuery, state: FSMContext):
    if isinstance(callback.message, types.Message):
        await state.update_data(lastMsgId=callback.message.message_id)
        await callback.message.edit_text(text='Введите логин.')
        await state.set_state(authStates.login)

    await callback.answer()

@ar.message(authStates.login, F.text)
async def waitingPassword(message: types.Message, state: FSMContext, bot: Bot):
    if isinstance(message, types.Message):
        await state.update_data(login=message.text)

        stateData = await state.get_data()
        lastMsgId = stateData.get('lastMsgId')

        await message.delete()
        await bot.edit_message_text(text='Введите пароль.', chat_id=message.chat.id, message_id=lastMsgId)
        await state.set_state(authStates.password)
        await state.update_data(lastMsgId=lastMsgId)

@ar.message(authStates.password, F.text)
async def checkingAcc(message: types.Message, state: FSMContext, bot: Bot):
    userData = await state.get_data()
    lastMsgId = userData.get('lastMsgId')
    login = userData['login']
    password = message.text or 'None'

    res = await authing(login, password)
    if isinstance(message, types.Message):
        if res is None:
            markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text='Попробовать еще', callback_data='auth')],
                [types.InlineKeyboardButton(text='Регистрация', callback_data='register')]
            ])
            await message.delete()
            await bot.edit_message_text(text='Пользователь не найден', chat_id=message.chat.id, message_id=lastMsgId, reply_markup=markup)
            await state.clear()
        else:
            markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text='Посмотреть мои пароли', callback_data='checkPasswords')]
            ])
            await state.set_state(userAccState.uid)
            await state.update_data(uId=res, chatId=message.chat.id, msgId=lastMsgId)
            await message.delete()
            await bot.edit_message_text(text='Успешная авторизация', chat_id=message.chat.id, message_id=lastMsgId, reply_markup=markup)

@ar.message(userAccState.uid, Command('uId'))
async def uId(message: types.Message, state: FSMContext):
    uIdData = await state.get_data()
    uId = uIdData.get('uId')
    await message.answer(text=f'{uId}')
