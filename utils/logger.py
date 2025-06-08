import logging
from config.settings import LOG_LEVEL, LOG_FILE


def setup_logger():
    """Настройка логирования для бота"""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('cat_meme_bot')


def log_command(user_id: int, username: str, command: str):
    """Логирование выполненной команды"""
    logger = logging.getLogger('cat_meme_bot')
    logger.info(f"User {user_id} (@{username}) executed command: {command}")


def log_callback(user_id: int, username: str, callback_data: str):
    """Логирование нажатия inline-кнопки"""
    logger = logging.getLogger('cat_meme_bot')
    logger.info(f"User {user_id} (@{username}) pressed button: {callback_data}")
