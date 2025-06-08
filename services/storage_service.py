import json
import os
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger('cat_meme_bot')

# Путь к файлу хранилища
STORAGE_DIR = Path(__file__).parent.parent / "storage"
FAVORITES_FILE = STORAGE_DIR / "favorites_storage.json"

class FavoritesStorage:
    """Класс для работы с локальным хранилищем избранных мемов"""
    
    def __init__(self):
        """Инициализация хранилища"""
        # Создаем директорию если не существует
        STORAGE_DIR.mkdir(exist_ok=True)
        self._ensure_storage_file()
    
    def _ensure_storage_file(self):
        """Убеждаемся что файл хранилища существует"""
        if not FAVORITES_FILE.exists():
            with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            logger.info(f"Создан файл хранилища: {FAVORITES_FILE}")
    
    def _load_data(self) -> Dict[str, Any]:
        """Загрузить данные из файла"""
        try:
            with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Ошибка при загрузке данных: {e}")
            return {}
    
    def _save_data(self, data: Dict[str, Any]) -> bool:
        """Сохранить данные в файл"""
        try:
            with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных: {e}")
            return False
    
    def add_favorite(self, user_id: int, meme_data: Dict[str, str]) -> bool:
        """
        Добавить мем в избранное пользователя
        
        Args:
            user_id: ID пользователя
            meme_data: Данные мема {"url": "...", "top": "...", "bottom": "..."}
        
        Returns:
            bool: True если успешно добавлено
        """
        try:
            data = self._load_data()
            user_key = str(user_id)
            
            # Инициализируем пользователя если не существует
            if user_key not in data:
                data[user_key] = {"favorites": []}
            
            # Проверяем что мем еще не в избранном
            favorites = data[user_key]["favorites"]
            for existing_meme in favorites:
                if (existing_meme.get("url") == meme_data.get("url") and 
                    existing_meme.get("top") == meme_data.get("top") and
                    existing_meme.get("bottom") == meme_data.get("bottom")):
                    logger.info(f"Мем уже в избранном пользователя {user_id}")
                    return False
            
            # Добавляем мем
            favorites.append(meme_data)
            
            # Ограничиваем количество избранных (максимум 50)
            if len(favorites) > 50:
                favorites.pop(0)  # Удаляем самый старый
            
            # Сохраняем
            if self._save_data(data):
                logger.info(f"Мем добавлен в избранное пользователя {user_id}")
                return True
            
        except Exception as e:
            logger.error(f"Ошибка при добавлении в избранное: {e}")
        
        return False
    
    def get_favorites(self, user_id: int) -> List[Dict[str, str]]:
        """
        Получить список избранных мемов пользователя
        
        Args:
            user_id: ID пользователя
        
        Returns:
            List: Список мемов пользователя
        """
        try:
            data = self._load_data()
            user_key = str(user_id)
            
            if user_key in data and "favorites" in data[user_key]:
                favorites = data[user_key]["favorites"]
                logger.info(f"Получено {len(favorites)} избранных мемов пользователя {user_id}")
                return favorites
            
        except Exception as e:
            logger.error(f"Ошибка при получении избранного: {e}")
        
        return []
    
    def remove_favorite(self, user_id: int, meme_index: int) -> bool:
        """
        Удалить мем из избранного по индексу
        
        Args:
            user_id: ID пользователя
            meme_index: Индекс мема в списке избранного
        
        Returns:
            bool: True если успешно удалено
        """
        try:
            data = self._load_data()
            user_key = str(user_id)
            
            if user_key in data and "favorites" in data[user_key]:
                favorites = data[user_key]["favorites"]
                
                if 0 <= meme_index < len(favorites):
                    removed_meme = favorites.pop(meme_index)
                    
                    if self._save_data(data):
                        logger.info(f"Мем удален из избранного пользователя {user_id}")
                        return True
            
        except Exception as e:
            logger.error(f"Ошибка при удалении из избранного: {e}")
        
        return False
    
    def get_favorites_count(self, user_id: int) -> int:
        """
        Получить количество избранных мемов пользователя
        
        Args:
            user_id: ID пользователя
        
        Returns:
            int: Количество избранных мемов
        """
        favorites = self.get_favorites(user_id)
        return len(favorites)
    
    def clear_favorites(self, user_id: int) -> bool:
        """
        Очистить все избранные мемы пользователя
        
        Args:
            user_id: ID пользователя
        
        Returns:
            bool: True если успешно очищено
        """
        try:
            data = self._load_data()
            user_key = str(user_id)
            
            if user_key in data:
                data[user_key]["favorites"] = []
                
                if self._save_data(data):
                    logger.info(f"Избранное очищено для пользователя {user_id}")
                    return True
            
        except Exception as e:
            logger.error(f"Ошибка при очистке избранного: {e}")
        
        return False


# Глобальный экземпляр хранилища
favorites_storage = FavoritesStorage()
