from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import reg

rr = Router()

class regStates(StatesGroup):
    login = State()
    password = State()

class userAccState(StatesGroup):
    uid = State()

@rr.callback_query(F.data == 'register')
async def auth(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    if isinstance(callback.message, types.Message):
        await state.update_data(lastMsgId=callback.message.message_id)
        await callback.message.edit_text(text='Введите логин.')
        await state.set_state(regStates.login)

    await callback.answer()

@rr.message(regStates.login, F.text)
async def waitingPassword(message: types.Message, state: FSMContext, bot: Bot):
    if isinstance(message, types.Message):
        await state.update_data(login=message.text)

        stateData = await state.get_data()
        lastMsgId = stateData.get('lastMsgId')

        await message.delete()
        await bot.edit_message_text(text='Введите пароль.', chat_id=message.chat.id, message_id=lastMsgId)
        await state.set_state(regStates.password)
        await state.update_data(lastMsgId=lastMsgId)

@rr.message(regStates.password, F.text)
async def checkingAcc(message: types.Message, state: FSMContext, bot: Bot):
    userData = await state.get_data()
    lastMsgId = userData.get('lastMsgId')
    login = userData['login']
    password = message.text or 'None'

    res = await reg(login, password)
    if isinstance(message, types.Message):
        if res is False:
            markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text='Попробовать еще', callback_data='register')]
            ])
            await message.delete()
            await bot.edit_message_text(text='Пользователь уже существует.', chat_id=message.chat.id, message_id=lastMsgId, reply_markup=markup)
            await state.clear()
        else:
            markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text='Посмотреть мои пароли', callback_data='checkPasswords')]
            ])
            await state.set_state(userAccState.uid)
            await state.update_data(uId=res, chatId=message.chat.id, msgId=lastMsgId)
            await message.delete()
            await bot.edit_message_text(text='Успешная регистрация', chat_id=message.chat.id, message_id=lastMsgId, reply_markup=markup)
