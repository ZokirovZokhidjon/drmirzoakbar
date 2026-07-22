import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# BotFather'дан олган токенингиз шу ерга қўйилди:
TOKEN = "8714433348:AAHJ1noXQ8OHokFk4_RYpbM22P6rseJoxjc"

# Ботдан келадиган хабарлар борадиган Telegram гуруҳингизнинг ID рақами
# (Агар гуруҳ ID'сини билмасангиз, гуруҳга @myidbot ёки шунга ўхшаш ID топдирадиган ботни қўшиб кўришингиз мумкин)
GROUP_ID = 1432886456 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Фойдаланувчи ҳолатлари (FSM)
class AppointmentState(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_issue = State()

# Асосий меню тугмалари
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🩺 Қабулга ёзилиш"), KeyboardButton(text="📍 Манзил ва Маълумот")],
            [KeyboardButton(text="👥 Telegram гуруҳга қўшилиш")]
        ],
        resize_keyboard=True
    )

# /start буйруғи
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Ассалому алайкум, {message.from_user.first_name}!\n"
        "Dr. MirzoAkbar MirMuxamedov қабулига онлайн ёзилиш ботига хуш келибсиз. Керакли тугмани танланг:",
        reply_markup=main_menu()
    )

# Телеграм гуруҳ тугмаси босилганда
@dp.message(F.text == "👥 Telegram гуруҳга қўшилиш")
async def get_group_link(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Гуруҳга ўтиш", url="https://t.me/+q8SbIRRx1ZAzOTI6")]
        ]
    )
    await message.answer("Бизнинг расмий Telegram гуруҳимизга қўшилиш учун қуйидаги тугмани босинг:", reply_markup=keyboard)

# Манзил тугмаси босилганда
@dp.message(F.text == "📍 Манзил ва Маълумот")
async def get_info(message: types.Message):
    await message.answer(
        "📍 **Манзил:** Наманган шаҳри\n"
        "🕒 **Иш вақти:** Душанба - Шанба, 09:00 - 18:00\n"
        "📞 **Телефон:** +998 (90) 260-52-66"
    )

# Қабулга ёзилиш жараёнини бошлаш
@dp.message(F.text == "🩺 Қабулга ёзилиш")
async def start_appointment(message: types.Message, state: FSMContext):
    await state.set_state(AppointmentState.waiting_for_name)
    await message.answer("Исм ва фамилиянгизни киритинг:")

# Исмни қабул қилиш
@dp.message(AppointmentState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    
    phone_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Рақамни юбориш", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await state.set_state(AppointmentState.waiting_for_phone)
    await message.answer("Телефон рақамингизни юборинг (пастдаги тугмани босинг ёки қўлда ёзинг):", reply_markup=phone_keyboard)

# Телефон рақамни қабул қилиш
@dp.message(AppointmentState.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone)
    
    await state.set_state(AppointmentState.waiting_for_issue)
    await message.answer("Қандай безовталик бор ёки қайси масалада мурожаат қилаяпсиз? Қисқача ёзиб қолдиринг:", reply_markup=types.ReplyKeyboardRemove())

# Муаммони қабул қилиш ва гуруҳга юбориш
@dp.message(AppointmentState.waiting_for_issue)
async def process_issue(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    name = user_data.get('name')
    phone = user_data.get('phone')
    issue = message.text
    
    group_message = (
        f"🚨 **ЯНГИ МУРОЖААТ (Қабулга ёзилиш)**\n\n"
        f"👤 **Исми:** {name}\n"
        f"📞 **Телефон:** {phone}\n"
        f"📝 **Шикоят/Муаммо:** {issue}\n"
        f"🔗 **Фойдаланувчи:** @{message.from_user.username if message.from_user.username else 'Йўқ'}"
    )
    
    try:
        await bot.send_message(GROUP_ID, group_message)
    except Exception as e:
        logging.error(f"Гуруҳга хабар юборишда хатолик: {e}")

    await state.clear()
    await message.answer(
        "Раҳмат! Сизнинг маълумотларингиз қабул қилинди ва шифокорга юборилди. Тез орада сиз билан боғланишади.",
        reply_markup=main_menu()
    )

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())