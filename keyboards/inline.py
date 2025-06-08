from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List


def get_random_cat_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для команды /randomcat"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🐱 Ещё кота!",
                    callback_data="more_cat"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎨 Создать мем с этим котом",
                    callback_data="create_meme_with_current"
                )
            ]
        ]
    )
    return keyboard


def get_meme_start_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для начала создания мема"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎲 Случайный кот",
                    callback_data="random_cat_for_meme"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="cancel_meme"
                )
            ]
        ]
    )
    return keyboard


def get_cat_selection_keyboard(cat_urls: List[str], start_index: int = 0) -> InlineKeyboardMarkup:
    """Клавиатура для выбора кота из списка"""
    keyboard = []
    
    # Показываем до 3 котов за раз
    end_index = min(start_index + 3, len(cat_urls))
    
    for i in range(start_index, end_index):
        keyboard.append([
            InlineKeyboardButton(
                text=f"🐱 Кот #{i + 1}",
                callback_data=f"select_cat_{i}"
            )
        ])
    
    # Навигация
    nav_row = []
    if start_index > 0:
        nav_row.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"cat_page_{start_index - 3}"
            )
        )
    if end_index < len(cat_urls):
        nav_row.append(
            InlineKeyboardButton(
                text="➡️ Далее",
                callback_data=f"cat_page_{end_index}"
            )
        )
    
    if nav_row:
        keyboard.append(nav_row)
    
    # Кнопка отмены
    keyboard.append([
        InlineKeyboardButton(
            text="❌ Отмена",
            callback_data="cancel_meme"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_meme_confirm_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для подтверждения создания мема"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Создать мем",
                    callback_data="confirm_meme"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Начать заново",
                    callback_data="restart_meme"
                )
            ]
        ]
    )
    return keyboard


def get_meme_result_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для готового мема"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⭐ Добавить в избранное",
                    callback_data="add_favorite"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎨 Создать ещё мем",
                    callback_data="new_meme"
                )
            ]
        ]
    )
    return keyboard


def get_favorites_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для просмотра избранного"""
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


def get_meme_keyboard() -> InlineKeyboardMarkup:
    """Общая клавиатура для мема"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Ещё раз",
                    callback_data="more_cat"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⭐ Добавить в избранное",
                    callback_data="add_favorite"
                )
            ]
        ]
    )
    return keyboard
