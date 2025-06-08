from aiogram.filters import BaseFilter
from aiogram.types import Message


class HasTextFilter(BaseFilter):
    """Фильтр для проверки наличия непустого текста в сообщении"""
    
    async def __call__(self, message: Message) -> bool:
        """
        Проверяет, содержит ли сообщение непустой текст
        
        Args:
            message (Message): Сообщение для проверки
            
        Returns:
            bool: True если сообщение содержит непустой текст, False в противном случае
        """
        return bool(message.text and message.text.strip())
