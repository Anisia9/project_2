from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_random_cat_keyboard, get_favorites_keyboard, get_meme_start_keyboard, get_meme_confirm_keyboard
from utils.logger import log_command
from services.api_client import get_random_cat_image, test_apis
from services.storage_service import favorites_storage
from states import MemeGenerationStates
import random

router = Router()

# Список URL-ов картинок котов (заглушки для демонстрации)
CAT_IMAGES_FALLBACK = [
    "https://cdn2.thecatapi.com/images/bpc.jpg",
    "https://cdn2.thecatapi.com/images/eac.jpg",
    "https://cdn2.thecatapi.com/images/dho.jpg",
    "https://cdn2.thecatapi.com/images/MTk3ODg4MA.jpg",
    "https://cdn2.thecatapi.com/images/cml.jpg"
]


@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    # Очищаем состояние при старте
    await state.clear()
    
    user = message.from_user
    if user:
        log_command(user.id, user.username or "unknown", "/start")
        user_name = user.first_name
    else:
        user_name = "пользователь"
    
    welcome_text = (
        f"Привет, {user_name}! 🐱\n\n"
        "Добро пожаловать в Cat Meme Bot!\n"
        "Я помогу тебе создавать мемы с котиками.\n\n"
        "Доступные команды:\n"
        "/help - справка по командам\n"
        "/randomcat - случайный котик\n"
        "/newmeme - создать мем\n"
        "/favorites - избранные мемы\n"
        "/test - проверить API\n\n"
        "Текст в мемах может быть только на английском языке!"
    )
    
    await message.answer(welcome_text)


@router.message(Command("help"))
async def help_command(message: Message):
    """Обработчик команды /help"""
    user = message.from_user
    if user:
        log_command(user.id, user.username or "unknown", "/help")
    
    help_text = (
        "📋 Справка по командам:\n\n"
        "/start - главное меню\n"
        "/help - эта справка\n"
        "/randomcat - получить случайную картинку кота\n"
        "/newmeme - создать мем с котом (FSM процесс)\n"
        "/favorites - посмотреть сохранённые мемы\n"
        "/test - проверить работу API\n\n"
        "🎨 Для создания мема:\n"
        "1. Выбери изображение кота\n"
        "2. Введи верхний текст\n"
        "3. Введи нижний текст\n"
        "4. Получи готовый мем!\n\n"
        "Используй inline-кнопки для навигации! 🐾\n\n"
        "Текст в мемах может быть только на английском языке!"
    )
    
    await message.answer(help_text)


@router.message(Command("randomcat"))
async def random_cat_command(message: Message):
    """Обработчик команды /randomcat"""
    user = message.from_user
    if user:
        log_command(user.id, user.username or "unknown", "/randomcat")
    
    # Пытаемся получить изображение из API
    cat_url = await get_random_cat_image()
    
    # Если API недоступно, используем заглушку
    if not cat_url:
        cat_url = random.choice(CAT_IMAGES_FALLBACK)
        caption = "🐱 Котик из кэша (API недоступно)"
    else:
        caption = "🐱 Случайный котик для тебя!"
    
    await message.answer_photo(
        photo=cat_url,
        caption=caption,
        reply_markup=get_random_cat_keyboard()
    )


@router.message(Command("newmeme"))
async def new_meme_command(message: Message, state: FSMContext):
    """Обработчик команды /newmeme"""
    user = message.from_user
    if user:
        log_command(user.id, user.username or "unknown", "/newmeme")
    
    # Устанавливаем состояние выбора изображения
    await state.set_state(MemeGenerationStates.choosing_image)
    
    await message.answer(
        "🎨 Создание мема с котом!\n\n"
        "Выбери, как хочешь получить изображение кота:",
        reply_markup=get_meme_start_keyboard()
    )


@router.message(Command("favorites"))
async def favorites_command(message: Message):
    """Обработчик команды /favorites"""
    user = message.from_user
    if user:
        log_command(user.id, user.username or "unknown", "/favorites")
    
    # Получаем список избранных мемов пользователя
    favorites = favorites_storage.get_favorites(user.id)
    
    if not favorites:
        favorites_text = (
            "⭐ Твои избранные мемы:\n\n"
            "Пока что список пуст.\n"
            "Создавай мемы и добавляй их в избранное!"
        )
        keyboard = get_favorites_keyboard()
    else:
        favorites_text = (
            f"⭐ Твои избранные мемы ({len(favorites)} шт.):\n\n"
            "Нажми кнопку ниже, чтобы просмотреть их!"
        )
        # Создаем расширенную клавиатуру с кнопкой просмотра
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="👀 Просмотреть мемы",
                        callback_data="view_favorites"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔄 Обновить список",
                        callback_data="refresh_favorites"
                    )
                ]
            ]
        )
    
    await message.answer(
        favorites_text,
        reply_markup=keyboard
    )


@router.message(Command("test"))
async def test_command(message: Message):
    """Обработчик команды /test - проверка API"""
    user = message.from_user
    if user:
        log_command(user.id, user.username or "unknown", "/test")
    
    await message.answer("🔍 Проверяю доступность API...")
      # Тестируем API
    results = await test_apis()
    status_text = "📊 Статус API:\n\n"
    status_text += f"🐱 The Cat API: {'✅ Работает' if results['cat_api'] else '❌ Недоступно'}\n"
    status_text += f"🎨 Memegen.link: {'✅ Работает' if results['memegen'] else '❌ Недоступно'}\n\n"
    
    working_apis = sum(results.values())
    if working_apis == len(results):
        status_text += "Все API работают нормально! 🎉"
    elif working_apis > 0:
        status_text += f"Работает {working_apis}/{len(results)} API. Бот адаптируется! 💪"
    else:
        status_text += "Все API недоступны. Бот будет использовать заглушки. 😿"
    
    await message.answer(status_text)

# FSM Text Handlers

@router.message(MemeGenerationStates.entering_top_text)
async def process_top_text(message: Message, state: FSMContext):
    """Обработка верхнего текста мема"""
    user = message.from_user
    if user:
        log_command(user.id, user.username or "unknown", f"top_text: {message.text}")
    
    if not message.text:
        await message.answer("❌ Пожалуйста, отправь текстовое сообщение!")
        return
    
    # Сохраняем верхний текст
    await state.update_data(top_text=message.text)
    await state.set_state(MemeGenerationStates.entering_bottom_text)
    
    await message.answer(
        f"✅ Верхний текст сохранён: '{message.text}'\n\n"
        "📝 Теперь введи нижний текст для мема:"
    )


@router.message(MemeGenerationStates.entering_bottom_text)
async def process_bottom_text(message: Message, state: FSMContext):
    """Обработка нижнего текста мема"""
    user = message.from_user
    if user:
        log_command(user.id, user.username or "unknown", f"bottom_text: {message.text}")
    
    if not message.text:
        await message.answer("❌ Пожалуйста, отправь текстовое сообщение!")
        return
    
    # Сохраняем нижний текст
    await state.update_data(bottom_text=message.text)
    
    # Получаем все данные
    data = await state.get_data()
    top_text = data.get("top_text", "")
    bottom_text = message.text
    image_url = data.get("selected_image")
    
    if not image_url:
        await message.answer(
            "❌ Изображение потеряно. Начни заново с /newmeme",
            reply_markup=get_meme_start_keyboard()
        )
        return
    
    # Показываем превью мема
    preview_text = (
        f"🎨 Превью мема:\n\n"
        f"📝 Верхний текст: '{top_text}'\n"
        f"📝 Нижний текст: '{bottom_text}'\n\n"
        f"Всё верно? Создаём мем?"
    )
    
    await message.answer(
        preview_text,
        reply_markup=get_meme_confirm_keyboard()
    )


@router.message(Command("cancel"))
async def cancel_command(message: Message, state: FSMContext):
    """Отменить текущий процесс FSM"""
    user = message.from_user
    if user:
        log_command(user.id, user.username or "unknown", "/cancel")
    
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("❌ Нет активного процесса для отмены.")
        return
    
    await state.clear()
    await message.answer(
        "❌ Процесс создания мема отменён.\n\n"
        "Используй /newmeme, чтобы начать заново."
    )
