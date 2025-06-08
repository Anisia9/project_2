import asyncio
import logging
import signal
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from config.settings import BOT_TOKEN
from utils.logger import setup_logger
from routers import commands
from routers.handlers import callbacks, favorites_handlers
from middlewares import LoggingMiddleware
from filters import HasTextFilter, HasImageFilter


async def set_bot_commands(bot: Bot):
    """Регистрация команд бота в меню Telegram"""
    commands_list = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Справка по командам"),
        BotCommand(command="randomcat", description="Случайный котик"),
        BotCommand(command="newmeme", description="Создать мем"),
        BotCommand(command="favorites", description="Избранные мемы"),
        BotCommand(command="test", description="Проверить API")
    ]
    
    await bot.set_my_commands(commands_list)


async def main():
    """Главная функция запуска бота"""
    # Настройка логирования
    logger = setup_logger()
    logger.info("Запуск Cat Meme Bot...")
    
    # Проверка токена
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не найден в переменных окружения!")
        return    # Создание бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрация команд в меню Telegram
    await set_bot_commands(bot)
    
    # Регистрация middleware
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    
    # Регистрация роутеров
    dp.include_router(commands.router)
    dp.include_router(callbacks.router)
    dp.include_router(favorites_handlers.router)
    
    # Запуск бота
    try:
        logger.info("Бот успешно запущен!")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания. Завершение работы бота...")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        logger.info("Закрытие сессии бота...")
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {e}")