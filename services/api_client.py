import aiohttp
import logging
from typing import Optional, List
from urllib.parse import quote
from collections import deque

logger = logging.getLogger('cat_meme_bot')

# Кэш для хранения последних изображений котов
cat_cache = deque(maxlen=10)

# Конфигурация API
CAT_API_URL = "https://api.thecatapi.com/v1/images/search"
MEMEGEN_BASE_URL = "https://api.memegen.link/images"


async def get_random_cat_image() -> Optional[str]:
    """Получить случайное изображение кота из The Cat API"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(CAT_API_URL, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and len(data) > 0:
                        cat_url = data[0]["url"]
                        # Добавляем в кэш
                        cat_cache.append(cat_url)
                        logger.info(f"Получено изображение кота: {cat_url}")
                        return cat_url
                else:
                    logger.error(f"The Cat API вернул статус: {response.status}")
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка сети при запросе к The Cat API: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при запросе к The Cat API: {e}")
    
    return None


async def get_multiple_cat_images(count: int = 5) -> List[str]:
    """Получить несколько изображений котов для выбора"""
    images = []
    try:
        async with aiohttp.ClientSession() as session:
            params = {"limit": count}
            async with session.get(CAT_API_URL, params=params, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    data = await response.json()
                    for item in data:
                        cat_url = item["url"]
                        images.append(cat_url)
                        cat_cache.append(cat_url)
                    logger.info(f"Получено {len(images)} изображений котов")
                else:
                    logger.error(f"The Cat API вернул статус: {response.status}")
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка сети при запросе к The Cat API: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при запросе к The Cat API: {e}")
    
    return images


def get_cached_cat_images() -> List[str]:
    """Получить изображения котов из кэша"""
    return list(cat_cache)


async def generate_meme_with_memegen(image_url: str, top_text: str, bottom_text: str) -> Optional[str]:
    """Генерировать мем через memegen.link с кастомным фоном (по документации)"""
    try:
        def clean_memegen_text(text):
            return (text.replace(" ", "_")
                        .replace("?", "~q")
                        .replace("&", "~a")
                        .replace("%", "~p")
                        .replace("#", "~h")
                        .replace("/", "~s")
                        .replace("\\", "~b")
                        .replace("<", "~l")
                        .replace(">", "~g")
                        .replace('"', "''"))
        clean_top = clean_memegen_text(top_text)
        clean_bottom = clean_memegen_text(bottom_text)
        meme_url = f"{MEMEGEN_BASE_URL}/custom/{clean_top}/{clean_bottom}.png?background={quote(image_url)}"
        async with aiohttp.ClientSession() as session:
            async with session.get(meme_url, timeout=aiohttp.ClientTimeout(total=20)) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'image' in content_type:
                        logger.info(f"Мем создан через memegen.link: {meme_url}")
                        return meme_url
    except Exception as e:
        logger.error(f"Ошибка при генерации мема через memegen.link: {e}")
    return None


async def download_meme_as_bytes(meme_url: str) -> Optional[bytes]:
    """Скачать мем как байты для Telegram"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(meme_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    if 'image' in content_type:
                        image_data = await response.read()
                        logger.info(f"Мем скачан как байты, размер: {len(image_data)} байт")
                        return image_data
                else:
                    logger.warning(f"Не удалось скачать мем: статус {response.status}")
    except Exception as e:
        logger.error(f"Ошибка при скачивании мема: {e}")
    return None


async def test_apis() -> dict:
    """Тестирование доступности API"""
    results = {
        "cat_api": False,
        "memegen": False
    }
    
    # Тест The Cat API
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(CAT_API_URL, timeout=aiohttp.ClientTimeout(total=5)) as response:
                results["cat_api"] = response.status == 200
    except:
        pass
    
    # Тест Memegen.link
    try:
        async with aiohttp.ClientSession() as session:
            test_url = "https://api.memegen.link/images/drake/test/api.png"
            async with session.get(test_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                results["memegen"] = response.status == 200
    except:
        pass
    
    return results


# Для обратной совместимости
async def generate_working_meme(image_url: str, top_text: str, bottom_text: str) -> Optional[str]:
    return await generate_meme_with_memegen(image_url, top_text, bottom_text)
