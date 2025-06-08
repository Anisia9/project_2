from aiogram.fsm.state import State, StatesGroup


class MemeGenerationStates(StatesGroup):
    """Состояния FSM для генерации мема"""
    choosing_image = State()  # Выбор изображения кота
    entering_top_text = State()  # Ввод верхней подписи
    entering_bottom_text = State()  # Ввод нижней подписи


# Кэш для хранения изображений котов (последние 10)
from collections import deque
cat_images_cache = deque(maxlen=10)
