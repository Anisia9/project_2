from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from utils.logger import log_callback, log_command
from services.storage_service import favorites_storage
from keyboards.inline import get_favorites_keyboard
from filters import HasTextFilter, HasImageFilter

router = Router()


@router.callback_query(F.data == "add_to_favorites")
async def add_to_favorites_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик добавления мема в избранное"""
    user = callback.from_user
    if user:
        log_callback(user.id, user.username or "unknown", "add_to_favorites")
    
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


@router.callback_query(F.data == "favorites_list")
async def favorites_list_handler(callback: CallbackQuery):
    """Обработчик возврата к списку избранного"""
    user = callback.from_user
    if user:
        log_callback(user.id, user.username or "unknown", "favorites_list")
    
    favorites = favorites_storage.get_favorites(user.id)
    
    if not favorites:
        try:
            if callback.message and hasattr(callback.message, 'photo') and callback.message.photo:
                # Если это сообщение с фото, отправляем новое текстовое сообщение
                await callback.message.answer(
                    "⭐ Твои избранные мемы:\n\n"
                    "Список пока пуст.\n"
                    "Создавай мемы и добавляй их в избранное!",
                    reply_markup=get_favorites_management_keyboard()
                )
            elif callback.message:
                # Если это текстовое сообщение, редактируем его
                await callback.message.edit_text(
                    "⭐ Твои избранные мемы:\n\n"
                    "Список пока пуст.\n"
                    "Создавай мемы и добавляй их в избранное!",
                    reply_markup=get_favorites_management_keyboard()
                )
        except Exception:
            # Если не получилось редактировать, отправляем новое
            if callback.message:
                await callback.message.answer(
                    "⭐ Твои избранные мемы:\n\n"
                    "Список пока пуст.\n"
                    "Создавай мемы и добавляй их в избранное!",
                    reply_markup=get_favorites_management_keyboard()
                )
        await callback.answer()
        return
    
    # Показываем список избранных мемов с кнопками навигации
    text = f"⭐ Твои избранные мемы ({len(favorites)}):\n\n"
    for i, meme in enumerate(favorites):
        top_text = meme.get("top", "")
        bottom_text = meme.get("bottom", "")
        text += f"{i + 1}. "
        if top_text or bottom_text:
            if top_text:
                text += f'"{top_text}"'
            if top_text and bottom_text:
                text += " / "
            if bottom_text:
                text += f'"{bottom_text}"'
        else:
            text += "Фото без текста"
        text += "\n"
    
    # Создаем клавиатуру со списком мемов
    keyboard = []
    for i in range(len(favorites)):
        keyboard.append([
            InlineKeyboardButton(
                text=f"👀 Мем {i + 1}",
                callback_data=f"favorite_show_{i}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(
            text="🎨 Создать новый мем",
            callback_data="new_meme"
        )
    ])
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    try:
        if callback.message and hasattr(callback.message, 'photo') and callback.message.photo:
            # Если это сообщение с фото, отправляем новое текстовое
            await callback.message.answer(
                text,
                reply_markup=reply_markup
            )
        elif callback.message:
            # Если это текстовое сообщение, редактируем его
            await callback.message.edit_text(
                text,
                reply_markup=reply_markup
            )
    except Exception:
        # Если не получилось редактировать, отправляем новое
        if callback.message:
            await callback.message.answer(
                text,
                reply_markup=reply_markup
            )
    
    await callback.answer()


@router.callback_query(F.data == "view_favorites")
async def view_favorites_handler(callback: CallbackQuery):
    """Обработчик просмотра избранных мемов"""
    user = callback.from_user
    if user:
        log_callback(user.id, user.username or "unknown", "view_favorites")
    
    favorites = favorites_storage.get_favorites(user.id)
    
    if not favorites:
        try:
            if callback.message.photo:
                # Если это сообщение с фото, отправляем новое текстовое сообщение
                await callback.message.answer(
                    "⭐ Твои избранные мемы:\n\n"
                    "Список пока пуст.\n"
                    "Создавай мемы и добавляй их в избранное!",
                    reply_markup=get_favorites_management_keyboard()
                )
            else:
                # Если это текстовое сообщение, редактируем его
                await callback.message.edit_text(
                    "⭐ Твои избранные мемы:\n\n"
                    "Список пока пуст.\n"
                    "Создавай мемы и добавляй их в избранное!",
                    reply_markup=get_favorites_management_keyboard()
                )
        except Exception:
            # Если не получилось редактировать, отправляем новое
            await callback.message.answer(
                "⭐ Твои избранные мемы:\n\n"
                "Список пока пуст.\n"
                "Создавай мемы и добавляй их в избранное!",
                reply_markup=get_favorites_management_keyboard()
            )
        await callback.answer()
        return
    
    # Показываем первый мем из избранного
    await show_favorite_meme(callback, favorites, 0)


@router.callback_query(F.data.startswith("favorite_"))
async def favorite_navigation_handler(callback: CallbackQuery):
    """Обработчик навигации по избранным мемам"""
    user = callback.from_user
    if user:
        log_callback(user.id, user.username or "unknown", f"favorite_navigation: {callback.data}")
    
    favorites = favorites_storage.get_favorites(user.id)
    
    if not favorites:
        await callback.answer("❌ Список избранного пуст", show_alert=True)
        return
    
    action = callback.data.split("_", 1)[1]
    
    if action.startswith("show_"):
        # Показать мем по индексу
        try:
            index = int(action.split("_", 1)[1])
            await show_favorite_meme(callback, favorites, index)
        except (ValueError, IndexError):
            await callback.answer("❌ Неверный индекс мема", show_alert=True)
    
    elif action.startswith("delete_"):
        # Удалить мем по индексу
        try:
            index = int(action.split("_", 1)[1])
            if favorites_storage.remove_favorite(user.id, index):
                await callback.answer("🗑️ Мем удален из избранного")
                # Обновляем список
                updated_favorites = favorites_storage.get_favorites(user.id)
                if updated_favorites:
                    # Показываем предыдущий мем или первый если удалили последний
                    new_index = min(index, len(updated_favorites) - 1)
                    await show_favorite_meme(callback, updated_favorites, new_index)
                else:
                    await view_favorites_handler(callback)
            else:
                await callback.answer("❌ Ошибка при удалении", show_alert=True)
        except (ValueError, IndexError):
            await callback.answer("❌ Неверный индекс мема", show_alert=True)
    elif action == "clear_all":
        # Очистить все избранное
        if favorites_storage.clear_favorites(user.id):
            if callback.message:
                try:
                    if callback.message.photo:
                        # Если это сообщение с фото, отправляем новое текстовое
                        await callback.message.answer(
                            "🗑️ Все избранные мемы удалены!\n\n"
                            "Создавай новые мемы и добавляй их в избранное!",
                            reply_markup=get_favorites_management_keyboard()
                        )
                    else:
                        # Если это текстовое сообщение, редактируем его
                        await callback.message.edit_text(
                            "🗑️ Все избранные мемы удалены!\n\n"
                            "Создавай новые мемы и добавляй их в избранное!",
                            reply_markup=get_favorites_management_keyboard()
                        )
                except Exception:
                    # Если не получилось редактировать, отправляем новое
                    await callback.message.answer(
                        "🗑️ Все избранные мемы удалены!\n\n"
                        "Создавай новые мемы и добавляй их в избранное!",
                        reply_markup=get_favorites_management_keyboard()
                    )
            await callback.answer("Избранное очищено")
        else:
            await callback.answer("❌ Ошибка при очистке", show_alert=True)


async def show_favorite_meme(callback: CallbackQuery, favorites: list, index: int):
    """Показать избранный мем по индексу"""
    if not (0 <= index < len(favorites)):
        await callback.answer("❌ Мем не найден", show_alert=True)
        return
    
    if not callback.message:
        await callback.answer("❌ Ошибка: сообщение недоступно", show_alert=True)
        return
    
    meme = favorites[index]
    meme_url = meme.get("url", "")
    top_text = meme.get("top", "")
    bottom_text = meme.get("bottom", "")
    created_at = meme.get("created_at", "")
    
    caption = f"⭐ Избранный мем {index + 1}/{len(favorites)}\n\n"
    if top_text:
        caption += f"📝 Верхний текст: {top_text}\n"
    if bottom_text:
        caption += f"📝 Нижний текст: {bottom_text}\n"
    if created_at:
        caption += f"📅 Создан: {created_at}\n"
    
    keyboard = get_favorite_meme_keyboard(index, len(favorites))
    
    # Отправляем новое сообщение с фото
    if meme_url:
        try:
            await callback.message.answer_photo(
                photo=meme_url,
                caption=caption,
                reply_markup=keyboard
            )
        except Exception:
            # Если не получается отправить фото, отправляем текст с ссылкой
            await callback.message.answer(
                f"{caption}\n🔗 Ссылка на мем: {meme_url}",
                reply_markup=keyboard
            )
    else:
        await callback.message.answer(
            caption,
            reply_markup=keyboard
        )
    
    await callback.answer()


def get_favorite_meme_keyboard(current_index: int, total_count: int) -> InlineKeyboardMarkup:
    """Клавиатура для просмотра избранного мема"""
    keyboard = []
    
    # Навигация
    nav_row = []
    if current_index > 0:
        nav_row.append(InlineKeyboardButton(
            text="⬅️ Предыдущий",
            callback_data=f"favorite_show_{current_index - 1}"
        ))
    if current_index < total_count - 1:
        nav_row.append(InlineKeyboardButton(
            text="➡️ Следующий", 
            callback_data=f"favorite_show_{current_index + 1}"
        ))
    
    if nav_row:
        keyboard.append(nav_row)
    
    # Действия с мемом
    keyboard.append([
        InlineKeyboardButton(
            text="🗑️ Удалить этот мем",
            callback_data=f"favorite_delete_{current_index}"
        )
    ])
    
    # Общие действия
    keyboard.append([
        InlineKeyboardButton(
            text="🎨 Создать новый мем",
            callback_data="new_meme"
        )    ])
    
    keyboard.append([
        InlineKeyboardButton(
            text="🔙 К списку избранного",
            callback_data="favorites_list"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_favorites_management_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для управления избранным"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Обновить список",
                    callback_data="view_favorites"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎨 Создать мем",
                    callback_data="new_meme"
                )
            ]
        ]
    )
    return keyboard


# Обработчики с использованием кастомных фильтров

@router.message(HasTextFilter())
async def handle_text_message(message: Message):
    """Обработчик сообщений с текстом (демонстрация фильтра HasTextFilter)"""
    user = message.from_user
    if user:
        log_command(user.id, user.username or "unknown", "text_message")
    
    # Простая обработка текстовых сообщений
    if message.text and any(word in message.text.lower() for word in ["кот", "котик", "мем", "помощь"]):
        await message.answer(
            "🐱 Я вижу, ты пишешь о котиках или мемах!\n"
            "Используй команды:\n"
            "/randomcat - случайный котик\n"
            "/newmeme - создать мем\n"
            "/help - все команды"
        )


@router.message(HasImageFilter())
async def handle_image_message(message: Message, state: FSMContext):
    """Обработчик сообщений с изображениями (демонстрация фильтра HasImageFilter)"""
    user = message.from_user
    if user:
        log_command(user.id, user.username or "unknown", "image_upload")
    
    # Проверяем наличие фото и получаем самое большое
    if not message.photo:
        return
        
    photo = message.photo[-1]
    
    # Сохраняем информацию о загруженном фото в состояние
    await state.update_data(uploaded_photo_id=photo.file_id)
    
    # Создаем клавиатуру для действий с загруженным фото
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎨 Создать мем из этого фото",
                    callback_data="create_meme_from_uploaded"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⭐ Добавить в избранное",
                    callback_data="add_photo_to_favorites"
                )
            ]
        ]
    )
    
    await message.answer(
        "📸 Отличное фото! Что хочешь с ним сделать?",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "create_meme_from_uploaded")
async def create_meme_from_uploaded_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик создания мема из загруженного фото"""
    user = callback.from_user
    if user:
        log_callback(user.id, user.username or "unknown", "create_meme_from_uploaded")
    
    data = await state.get_data()
    photo_id = data.get("uploaded_photo_id")
    
    if not photo_id:
        await callback.answer("❌ Фото не найдено", show_alert=True)
        return
    
    await callback.answer("🎨 Переходим к созданию мема...")
    
    # Устанавливаем состояние для создания мема и сохраняем ID фото
    from states import MemeGenerationStates
    await state.set_state(MemeGenerationStates.entering_top_text)
    await state.update_data(selected_image=photo_id, is_uploaded_photo=True)
    
    if callback.message:
        await callback.message.answer(
            "🎨 Создание мема из твоего фото!\n\n"
            "Напиши верхний текст для мема:"
        )


@router.callback_query(F.data == "add_photo_to_favorites")
async def add_uploaded_photo_to_favorites_handler(callback: CallbackQuery, state: FSMContext):
    """Обработчик добавления загруженного фото в избранное"""
    user = callback.from_user
    if user:
        log_callback(user.id, user.username or "unknown", "add_photo_to_favorites")
    
    data = await state.get_data()
    photo_id = data.get("uploaded_photo_id")
    
    if not photo_id:
        await callback.answer("❌ Фото не найдено", show_alert=True)
        return
    
    # Подготавливаем данные фото для избранного
    photo_data = {
        "url": photo_id,  # Для загруженных фото сохраняем file_id
        "top": "",
        "bottom": "",
        "created_at": str(callback.message.date) if callback.message else "",
        "is_uploaded": True
    }
    
    # Добавляем в избранное
    if favorites_storage.add_favorite(user.id, photo_data):
        await callback.answer("⭐ Фото добавлено в избранное!", show_alert=True)
    else:
        await callback.answer("⚠️ Фото уже в избранном или произошла ошибка", show_alert=True)
