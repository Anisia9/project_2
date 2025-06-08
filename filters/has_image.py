from aiogram.filters import BaseFilter
from aiogram.types import Message


class HasImageFilter(BaseFilter):
    """Фильтр для проверки наличия фотографии в сообщении"""
    
    async def __call__(self, message: Message) -> bool:
        """
        Проверяет, содержит ли сообщение фотографию
        
        Args:
            message (Message): Сообщение для проверки
            
        Returns:
            bool: True если сообщение содержит фото, False в противном случае
        """
        return bool(message.photo)
