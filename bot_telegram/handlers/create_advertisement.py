from aiogram import types
from aiogram.dispatcher import FSMContext
from ..loader import dp, bot
from .states import AuthState, SearchState, SearchStateUn
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery, InputFile
from .api_queries import check_user, register_user, post_words, get_result, result, delete_keywords, get_user_data
from ..keyboards.choise_buttons import choice, choice2
import datetime, re
import math


data_for_registration = {}
now = datetime.date.today()
tel_id = []


@dp.message_handler(Command('start'))
async def answer(message: types.Message):
    username = message.from_user.full_name
    telegram_id = message.from_user.id
    tel_id.append(telegram_id)
    await message.answer(f'Здравствуйте, {username} ✋')
    check = await check_user(telegram_id)
    if check == 400:
        await message.answer('Извините, сервер не отвечает. Повторите попытку позднее ⚠')
    if not check:
        await message.answer('Вы не зарегистрированы\n'
                            '1️⃣ Укажите ваше имя'
    )
        await AuthState.name.set()
    else:
        try:
            res = await result({'telegram_id': telegram_id})
            if res:
                await message.answer('Ключевые слова, по которым вы делали поиск:')       
                text = ''
                for key, value in res.items():
                    text += '{key}. <b>{value}</b>\n'.format(key=key, value=value)
                await message.answer(text, reply_markup=choice2)
            else:
                await SearchState.key_words.set()
                await message.answer('Введите ключевые слова через запятую')
        except AttributeError:
            await message.answer('Ошибка. Нажмите /start, чтобы повторить попытку ⚠')


@dp.callback_query_handler(text_contains='delete')
async def del_keywords(call: CallbackQuery):
    await call.answer(cache_time=60)
    result = await delete_keywords({'telegram_id':tel_id[-1]})
    await call.message.answer('Ключевые слова удалены\n'
                                'Введите новые через запятую'
                                )


@dp.callback_query_handler(text_contains='add')
async def add_keywords(call: CallbackQuery):
    await call.answer(cache_time=60)
    await SearchState.key_words.set()
    await call.message.answer('Введите новые через запятую')


# @dp.callback_query_handler(text_contains='search')
# async def search_keywords(call: CallbackQuery, state: FSMContext):
#     await call.answer(cache_time=60)
#     # await SearchState.key_words.set()
#     await SearchState.next()


@dp.message_handler(state=SearchState.key_words)    
async def get_key_words(message: types.Message, state: FSMContext):
    key_words = message.text
    await state.update_data(key_words=key_words)
    data = await state.get_data()
    telegram_id = message.from_user.id
    data['telegram_id'] = telegram_id
    result = await post_words(data)
    await message.answer('Идет поиск по ключевым словам... 🔍')
    res = await get_result(data)
    user_data = await get_user_data({'telegram_id': telegram_id})
    if not user_data or not res:
        await message.answer('Извините, сервер не отвечает. Повторите попытку позднее ⚠')
        return
    name = user_data['name']
    patronymic = user_data['patronymic']
    surname = user_data['surname']
    pdf = InputFile(path_or_bytesio=f'bot_telegram/handlers/reports/{name} {patronymic} {surname} от {now}.pdf')
    await bot.send_document(telegram_id, pdf)
    await message.answer('Отчет предоставлен 📋')


@dp.message_handler(state=AuthState.name)    
async def save_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await AuthState.next()
    await message.answer(text="2️⃣ Введите вашу фамилию")


@dp.message_handler(state=AuthState.surname)    
async def save_surname(message: types.Message, state: FSMContext):
    surname = message.text
    await state.update_data(surname=surname)
    await AuthState.next()
    await message.answer(text="3️⃣ Введите ваше отчество")


@dp.message_handler(state=AuthState.patronymic)    
async def save_patronymic(message: types.Message, state: FSMContext):
    patronymic = message.text
    await state.update_data(patronymic=patronymic)
    await message.answer(text="4️⃣ Введите вашу дату рождения в формате 'ДД.ММ.ГГГГ'")


@dp.message_handler(state=AuthState.date_of_birth)    
async def save_date_of_birth(message: types.Message, state: FSMContext):
    date_of_birth = message.text
    pattern = r'^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]|(?:Jan|Mar|May|Jul|Aug|Oct|Dec)))\1|(?:(?:29|30)(\/|-|\.)(?:0?[1,3-9]|1[0-2]|(?:Jan|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)(?:0?2|(?:Feb))\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9]|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep))|(?:1[0-2]|(?:Oct|Nov|Dec)))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$'
    # pattern = r'\d{2}.\d{2}.\d{4}'
    result = re.findall(pattern, date_of_birth)
    if not result:
        await message.answer(text="Неверный формат даты ⚠")
        return 
    await state.update_data(date_of_birth=date_of_birth)
    await AuthState.next()
    await message.answer(text="5️⃣ Введите ваш номер телефона")


@dp.message_handler(state=AuthState.phone)    
async def save_phone(message: types.Message, state: FSMContext):
    phone = message.text
    try:
        int(phone)
    except:
        await message.answer(text="Неверный формат номера ⚠") 
        return 
    await state.update_data(phone=phone)
    await AuthState.next()
    await message.answer(text="6️⃣ Введите город")


@dp.message_handler(state=AuthState.city)    
async def save_city(message: types.Message, state: FSMContext):
    city = message.text
    await state.update_data(city=city)
    data = await state.get_data()
    telegram_id = message.from_user.id
    data['telegram_id'] = telegram_id
    data_for_registration.setdefault(telegram_id, data)
    name = data['name']
    surname = data['surname']
    patronymic = data['patronymic']
    phone = data['phone']
    date_of_birth = data['date_of_birth']
    city = data['city']
    await state.finish()
    await message.answer(
        'Введенные данные верны?\n\n'
        f'1️⃣ Имя: <b>{name}</b>\n'
        f'2️⃣ Фамилия: <b>{surname}</b>\n'
        f'3️⃣ Отчество: <b>{patronymic}</b>\n'
        f'4️⃣ Телефон: <b>{phone}</b>\n'
        f'5️⃣ Дата рождения: <b>{date_of_birth}</b>\n'
        f'6️⃣ Город: <b>{city}</b>'
        , reply_markup=choice)


@dp.callback_query_handler(text_contains='accept')
async def accept_data(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await call.message.answer('Укажите через запятую ключевые слова для поиска 🔠')
    await SearchStateUn.key_words.set()


@dp.callback_query_handler(text_contains='reject')
async def accept_data(call: CallbackQuery):
    await call.message.answer('Чтобы пройти заново, нажмите /start')


@dp.message_handler(state=SearchStateUn.key_words)
async def get_key_words(message: types.Message, state: FSMContext):
    key_words = message.text
    await state.update_data(key_words=key_words)
    data = await state.get_data()
    telegram_id = message.from_user.id
    data['telegram_id'] = telegram_id
    await register_user(data_for_registration[telegram_id])
    await message.answer(data_for_registration[telegram_id])
    await post_words(data)
    await SearchStateUn.next()
    await message.answer('Идет поиск по ключевым словам... 🔍')
    await get_result(data)
    user_data = data_for_registration[telegram_id]
    name = user_data['name']
    patronymic = user_data['patronymic']
    surname = user_data['surname']
    pdf = InputFile(path_or_bytesio=f'bot_telegram/handlers/reports/{name} {patronymic} {surname} от {now}.pdf')
    await bot.send_document(telegram_id, pdf)
    await message.answer('Отчет предоставлен 📋')
    await message.answer('Сколько раз в месяц вы бы хотели получать отчет? 🕢')


@dp.message_handler(state=SearchStateUn.amount)
async def get_amount(message: types.Message, state: FSMContext):
    amount = message.text
    telegram_id = message.from_user.id
    try:
        amount = int(amount)
    except ValueError:
        await message.answer('Введите числовое значение ⚠')
        return
    if amount < 1:
        await message.answer('Значение не может быть меньше 1 ⚠')
        return
    elif amount > 30:
        await message.answer('Значение не может быть больше 30 ⚠')
        return
    await state.update_data(amount=amount)
    await message.answer(f'Данные получены. Каждые {round(30/amount)} дней, вам будет предоставляться отчет 📋📅')
    await message.answer('До свидания! 🤚')
    data_for_registration.pop(telegram_id)




