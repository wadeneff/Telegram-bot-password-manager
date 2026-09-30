from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import editPassword, getPassword
from handlers.register import userAccState

hr = Router()

class states(StatesGroup):
    waitingPassword = State()

@hr.callback_query(F.data == 'clear')
async def clear(callback: types.CallbackQuery, state: FSMContext):
    if isinstance(callback.message, types.Message):
        await callback.message.delete()
    await state.clear()

@hr.callback_query(userAccState.uid, F.data == 'checkPasswords')
async def checkPasswords(callback: types.CallbackQuery, state: FSMContext):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='Telegram', callback_data='tg'), types.InlineKeyboardButton(text='VK', callback_data='vk')],
        [types.InlineKeyboardButton(text='Discord', callback_data='dis'), types.InlineKeyboardButton(text='Steam', callback_data='steam')],
        [types.InlineKeyboardButton(text='Google', callback_data='google'), types.InlineKeyboardButton(text='Yandex', callback_data='yandex')],
        [types.InlineKeyboardButton(text='Другое', callback_data='other')],
        [types.InlineKeyboardButton(text='Другое #1', callback_data='other1')],
        [types.InlineKeyboardButton(text='Другое #2', callback_data='other2')],
        [types.InlineKeyboardButton(text='Другое #3', callback_data='other3')],
        [types.InlineKeyboardButton(text='Другое #4', callback_data='other4')],
        [types.InlineKeyboardButton(text='Другое #5', callback_data='other5')],
        [types.InlineKeyboardButton(text='Выход', callback_data='clear')]
    ])
    if isinstance(callback.message, types.Message):
        await callback.message.delete()
        msg = await callback.message.answer(text='Главное меню.', reply_markup=markup)
        await state.update_data(msgId=msg.message_id, chatId = callback.message.chat.id)
    await callback.answer()

@hr.callback_query(userAccState.uid, F.data.in_({
    'tg', 'vk', 'dis', 'steam', 'google', 'yandex',
    'other', 'other1', 'other2', 'other3', 'other4', 'other5'
}))
async def checkAccPassword(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='Редактировать', callback_data='editPassword')],
        [types.InlineKeyboardButton(text='Назад', callback_data='checkPasswords')]
    ])

    data = await state.get_data()
    aId = data.get('uId')
    chatId = data.get('chatId')
    msgId = data.get('msgId')

    if aId is None:
        await bot.edit_message_text(text='Ошибка состояния.', chat_id=chatId, message_id=msgId, reply_markup=markup)
        return

    social = callback.data

    if social is None:
        await bot.edit_message_text(text='Ошибка выбора сервиса.', chat_id=chatId, message_id=msgId, reply_markup=markup)
        return

    password = await getPassword(aId, social)
    if not password:
        password = "Пароль не установлен"

    if isinstance(callback.message, types.Message):
        await state.update_data(social=f'{social}')
        await callback.message.edit_text(
            text=f'Ваш пароль от {social.upper()}:\n<tg-spoiler>{password}</tg-spoiler>',
            reply_markup=markup,
            parse_mode="HTML"
        )

    await callback.answer()

@hr.callback_query(userAccState.uid, F.data == 'editPassword')
async def tryGetNewPassword(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='Назад', callback_data='checkPasswords')]
    ])

    data = await state.get_data()
    aId = data.get('uId')
    social = data.get('social')
    chatId = data.get('chatId')
    msgId = data.get('msgId')

    await state.set_state(states.waitingPassword)
    await state.update_data(social=social, aId=aId, msgId=msgId, chatId=chatId)

    await bot.edit_message_text(text='Введите новый пароль', chat_id=chatId, message_id=msgId, reply_markup=markup)

    await callback.answer()

@hr.message(states.waitingPassword, F.text)
async def accessToSetNewPassword(message: types.Message, state: FSMContext, bot: Bot):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='Да', callback_data='setNewPassword'), types.InlineKeyboardButton(text='Нет', callback_data='checkPasswords')]
    ])
    newPassword = message.text

    data = await state.get_data()
    social = data.get('social')
    chatId = data.get('chatId')
    msgId = data.get('msgId')

    await state.update_data(password=newPassword)

    await message.delete()

    if social is None:
        await bot.edit_message_text(text='Ошибка выбора сервиса.', chat_id=chatId, message_id=msgId, reply_markup=markup)
        return
    await bot.edit_message_text(text=f'Вы уверены что хотите установить пароль <tg-spoiler>{newPassword}</tg-spoiler> для {social.upper()}?', chat_id=chatId, message_id=msgId, reply_markup=markup, parse_mode="HTML")

@hr.callback_query(states.waitingPassword, F.data == 'setNewPassword')
async def setNewPassword(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    aId = data.get('uId')
    social = data.get('social')
    chatId = data.get('chatId')
    msgId = data.get('msgId')
    password = data.get('password')

    if aId is None:
        markup = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text='Назад', callback_data='checkPasswords')]
        ])
        await bot.edit_message_text(text='Ошибка пользовательского ID', chat_id=chatId, message_id=msgId, reply_markup=markup)
        await state.set_state(userAccState.uid)
        await state.update_data(aId=aId)
        await callback.answer()
        return
    if social is None:
        markup = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text='Назад', callback_data='checkPasswords')]
        ])
        await bot.edit_message_text(text='Ошибка выбора сервиса', chat_id=chatId, message_id=msgId, reply_markup=markup)
        await state.set_state(userAccState.uid)
        await state.update_data(aId=aId)
        await callback.answer()
        return
    if password is None:
        markup = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text='Назад', callback_data='checkPasswords')]
        ])
        await bot.edit_message_text(text='Ошибка инициализации пароля', chat_id=chatId, message_id=msgId, reply_markup=markup)
        await state.set_state(userAccState.uid)
        await state.update_data(aId=aId)
        await callback.answer()
        return

    await editPassword(aId, social, password)
    markup = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='Назад', callback_data='checkPasswords')]
    ])
    await state.set_state(userAccState.uid)
    await state.update_data(uId=aId)
    await bot.edit_message_text(text='Пароль был изменен', chat_id=chatId, message_id=msgId, reply_markup=markup)
    await callback.answer()
