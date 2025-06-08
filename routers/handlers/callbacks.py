from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from keyboards.inline import (
    get_random_cat_keyboard, 
    get_favorites_keyboard, 
    get_meme_start_keyboard,
    get_meme_result_keyboard,
    get_meme_confirm_keyboard
)
from utils.logger import log_callback
from services.api_client import get_random_cat_image, cat_cache, download_meme_as_bytes, generate_working_meme
from services.storage_service import favorites_storage
from states import MemeGenerationStates
import random

router = Router()


@router.callback_query(F.data == "more_cat")
async def more_cat_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Ещё кота!'"""
    user = callback.from_user
    if user:
        log_callback(user.id, user.username or "unknown", "more_cat")
    
    # Получаем новую случайную картинку через API
    cat_url = await get_random_cat_image()
    
    if cat_url:
        # Отправляем новую картинку
        if callback.message:
            await callback.message.answer_photo(
                photo=cat_url,
                caption="🐱 Ещё один котик для тебя!",
                reply_markup=get_random_cat_keyboard()
            )
        await callback.answer("Новый котик загружен! 🐾")
    else:
        await callback.answer("❌ Не удалось загрузить нового котика", show_alert=True)


@router.callback_query(F.data == "create_meme_with_current")
async def create_meme_with_current_callback(callback: CallbackQuery, state: FSMContext):
    """Создать мем с текущим котом"""
    user = callback.from_user
    if user:
        log_callback(user.id, user.username or "unknown", "create_meme_with_current")
    
    # Получаем последнее изображение из кэша
    cached_images = list(cat_cache)
    if cached_images:
        selected_image = cached_images[-1]  # Берем последнее изображение
        await state.update_data(selected_image=selected_image)
        await state.set_state(MemeGenerationStates.entering_top_text)
        
        if callback.message:
            await callback.message.answer(
                "🎨 Отлично! Теперь введи верхний текст для мема:"
            )
        await callback.answer()
    else:
        await callback.answer("❌ Изображение не найдено в кэше", show_alert=True)


@router.callback_query(F.data == "random_cat_for_meme")
async def random_cat_for_meme_callback(callback: CallbackQuery, state: FSMContext):
    """Выбрать случайного кота для мема"""
    user = callback.from_user
    if user:
        log_callback(user.id, user.username or "unknown", "random_cat_for_meme")
    
    cat_url = await get_random_cat_image()
    if cat_url:
        await state.update_data(selected_image=cat_url)
        await state.set_state(MemeGenerationStates.entering_top_text)
        
        if callback.message:
            await callback.message.answer_photo(
                photo=cat_url,
                caption="🎨 Котик выбран! Теперь введи верхний текст для мема:"
            )
        await callback.answer()
    else:
        await callback.answer("❌ Не удалось загрузить изображение", show_alert=True)


@router.callback_query(F.data == "confirm_meme")
async def confirm_meme_callback(callback: CallbackQuery, state: FSMContext):
    """Подтвердить создание мема"""
    user = callback.from_user
    if user:
        log_callback(user.id, user.username or "unknown", "confirm_meme")
    
    data = await state.get_data()
    image_url = data.get("selected_image")
    top_text = data.get("top_text", "")
    bottom_text = data.get("bottom_text", "")
    
    if not image_url:
        await callback.answer("❌ Изображение не найдено", show_alert=True)
        return
    
    await callback.answer("🎨 Создаю мем...")
    
    # Генерируем мем
    meme_url = await generate_working_meme(image_url, top_text, bottom_text)
    
    if meme_url:
        # Сохраняем URL созданного мема в состоянии для возможности добавления в избранное
        await state.update_data(last_meme_url=meme_url)
        
        if callback.message:
            try:
                # Пытаемся отправить изображение по URL
                await callback.message.answer_photo(
                    photo=meme_url,
                    caption=f"🎉 Твой мем готов!\n\n📝 Верхний текст: {top_text}\n📝 Нижний текст: {bottom_text}",
                    reply_markup=get_meme_result_keyboard()
                )
            except Exception as e:
                # Если URL не работает, пробуем скачать и отправить как файл
                try:
                    meme_bytes = await download_meme_as_bytes(meme_url)
                    if meme_bytes:
                        meme_file = BufferedInputFile(meme_bytes, filename="meme.png")
                        await callback.message.answer_photo(
                            photo=meme_file,
                            caption=f"🎉 Твой мем готов!\n\n📝 Верхний текст: {top_text}\n📝 Нижний текст: {bottom_text}",
                            reply_markup=get_meme_result_keyboard()
                        )
                    else:
                        raise Exception("Не удалось скачать изображение")
                except Exception as e2:
                    # Если и это не работает, отправляем ссылку
                    await callback.message.answer(
                        f"🎉 Твой мем готов!\n\n"
                        f"📝 Верхний текст: {top_text}\n"
                        f"📝 Нижний текст: {bottom_text}\n\n"
                        f"🔗 Ссылка на мем: {meme_url}\n\n"
                        f"⚠️ Telegram не смог загрузить изображение, "
                        f"но ты можешь открыть ссылку и сохранить мем.",
                        reply_markup=get_meme_result_keyboard()
                    )
        # НЕ очищаем состояние сразу, чтобы можно было добавить в избранное
        # Состояние очистится при создании нового мема или отмене
    else:
        if callback.message:
            await callback.message.answer(
                "❌ Не удалось создать мем. Попробуй ещё раз.",
                reply_markup=get_meme_start_keyboard()
            )


@router.callback_query(F.data == "cancel_meme")
async def cancel_meme_callback(callback: CallbackQuery, state: FSMContext):
    """Отменить создание мема"""
    user = callback.from_user
    if user:
        log_callback(user.id, user.username or "unknown", "cancel_meme")
    
    await state.clear()
    
    if callback.message:
        await callback.message.answer(
            "❌ Создание мема отменено.\n\nИспользуй /newmeme, чтобы начать заново."
        )
    await callback.answer("❌ Создание мема отменено")


@router.callback_query(F.data == "new_meme")
async def new_meme_callback(callback: CallbackQuery, state: FSMContext):
    """Создать новый мем"""
    user = callback.from_user
    if user:
        log_callback(user.id, user.username or "unknown", "new_meme")
    
    await state.clear()
    
    if callback.message:
        await callback.message.answer(
            "🎨 Давай создадим новый мем!\n\nВыбери источник изображения:",
            reply_markup=get_meme_start_keyboard()
        )
    await callback.answer()


@router.callback_query(F.data == "add_favorite")
async def add_favorite_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Добавить в избранное'"""
    user = callback.from_user
    if user:
        log_callback(user.id, user.username or "unknown", "add_favorite")
    
    # Получаем данные текущего мема из состояния
    data = await state.get_data()
    image_url = data.get("selected_image")
    top_text = data.get("top_text", "")
    bottom_text = data.get("bottom_text", "")
    meme_url = data.get("last_meme_url")  # URL созданного мема
    
    if not (image_url or meme_url):
        await callback.answer("❌ Нет мема для добавления в избранное", show_alert=True)
        return
    
    # Подготавливаем данные мема
    meme_data = {
        "url": meme_url or image_url,
        "top": top_text,
        "bottom": bottom_text,
        "created_at": str(callback.message.date) if callback.message else ""
    }
    
    # Добавляем в избранное
    if favorites_storage.add_favorite(user.id, meme_data):
        await callback.answer("⭐ Мем добавлен в избранное!", show_alert=True)
    else:
        await callback.answer("⚠️ Мем уже в избранном или произошла ошибка", show_alert=True)


@router.callback_query(F.data == "refresh_favorites")
async def refresh_favorites_callback(callback: CallbackQuery):
    """Обработчик кнопки 'Обновить список' в избранном"""
    user = callback.from_user
    if user:
        log_callback(user.id, user.username or "unknown", "refresh_favorites")
    
    # Получаем список избранных мемов
    favorites = favorites_storage.get_favorites(user.id)
    
    if not favorites:
        updated_text = (
            "⭐ Твои избранные мемы (обновлено):\n\n"
            "Список пока пуст.\n"
            "Создавай мемы и добавляй их в избранное!"
        )
    else:
        updated_text = (
            f"⭐ Твои избранные мемы ({len(favorites)} шт.):\n\n"
            "Нажми кнопку ниже, чтобы просмотреть их!"
        )
    
    keyboard = get_favorites_keyboard()
    if favorites:
        # Добавляем кнопку для просмотра мемов
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
    
    if callback.message:
        try:
            await callback.message.edit_text(
                updated_text,
                reply_markup=keyboard
            )
        except Exception:
            await callback.message.answer(
                updated_text,
                reply_markup=keyboard
            )
    
    await callback.answer("Список обновлён! 🔄")
