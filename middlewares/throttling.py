from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
import logging
import datetime
from typing import Callable, Dict, Any, Awaitable


class LoggingMiddleware(BaseMiddleware):
    """Middleware для логирования всех входящих апдейтов"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Получаем информацию об апдейте
        update_type = "unknown"
        user_id = None
        
        if isinstance(event, Update):
            if event.message:
                update_type = "message"
                user_id = event.message.from_user.id if event.message.from_user else None
            elif event.callback_query:
                update_type = "callback_query"
                user_id = event.callback_query.from_user.id if event.callback_query.from_user else None
            elif event.inline_query:
                update_type = "inline_query"
                user_id = event.inline_query.from_user.id if event.inline_query.from_user else None
        
        # Логируем информацию об апдейте
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] Update: {update_type}, User ID: {user_id}"
        
        # Логируем в файл bot.log
        logger = logging.getLogger("bot")
        logger.info(log_message)
        
        # Вызываем следующий обработчик
        return await handler(event, data)
