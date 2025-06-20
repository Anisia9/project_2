# Telegram Cat Meme Bot

Полнофункциональный Telegram-бот для генерации и управления мемами с котами. Использует The Cat API для получения изображений котов и Memegen.link для создания мемов с пользовательским текстом.

## Автор

Гришко Анисья Антоновна ИСУ: 465660

## Функционал

### Команды
- `/start` — приветственное сообщение с описанием всех возможностей
- `/help` — подробная справка по всем командам и функциям
- `/randomcat` — получение случайной картинки кота с интерактивными кнопками
- `/newmeme` — запуск процесса создания мема через FSM состояния
- `/favorites` — управление избранными мемами (просмотр, удаление, навигация)
- `/test` — проверка доступности внешних API (The Cat API, Memegen.link)

### Интерактивные элементы

#### Inline-кнопки:
- **Ещё кота!** — получение нового случайного изображения
- **Добавить в избранное** — сохранение текущего мема/изображения
- **Создать мем** — переход к созданию мема из текущего изображения
- **Избранное** — просмотр сохраненных мемов
- **Обновить список** — обновление списка избранного
- **Удалить** — удаление конкретного мема из избранного
- **Навигация** — переключение между избранными мемами

#### FSM Состояния для создания мемов:
1. **Выбор изображения** — выбор случайного кота или загрузка собственного
2. **Ввод верхнего текста** — добавление текста в верхнюю часть мема
3. **Ввод нижнего текста** — добавление текста в нижнюю часть мема
4. **Предпросмотр и подтверждение** — финальный просмотр перед созданием

### Технические возможности

#### Middleware:
- **LoggingMiddleware** — автоматическое логирование всех входящих обновлений
- Запись user_id, типа события и времени в файл `bot.log`

#### Кастомные фильтры:
- **HasTextFilter** — обработка только сообщений с непустым текстом
- **HasImageFilter** — обработка только сообщений с изображениями
- Автоматическое предложение действий для загруженных изображений

#### Система хранения:
- **Локальное JSON хранилище** для избранных мемов
- **Поддержка множественных пользователей** с индивидуальными коллекциями
- **Автоматическое сохранение** при каждом изменении

### Логирование и мониторинг
- **Полное логирование** всех действий пользователей
- **Детальные логи** с информацией о времени, пользователе и типе события
- **Логирование ошибок** API и внутренних исключений
- **Ротация логов** с временными метками

## Архитектура проекта

```
c:\coding\Anliiia-sem2-proj2\
├── bot.py                     # Точка входа и инициализация бота
├── requirements.txt           # Зависимости проекта
├── README.md                  # Документация
├── bot.log                    # Файл логов
├── .env.example               # Переменные окружения
│
├── config/                    # Конфигурация
│   ├── __init__.py
│   └── settings.py            # Настройки бота и API ключи
│
├── routers/                   # Маршрутизация
│   ├── __init__.py
│   ├── commands.py            # Основные команды (/start, /help, etc.)
│   └── handlers/
│       ├── __init__.py
│       ├── callbacks.py       # Обработчики callback запросов
│       └── favorites_handlers.py  # Управление избранным
│
├── keyboards/                 # Интерфейс
│   ├── __init__.py
│   └── inline.py              # Inline клавиатуры
│
├── services/                  # Внешние сервисы
│   ├── api_client.py          # Интеграция с The Cat API и Memegen
│   └── storage_service.py     # Управление локальным хранилищем
│
├── middlewares/               # Промежуточное ПО
│   ├── __init__.py
│   └── throttling.py          # Логирование и антиспам
│
├── filters/                   # Кастомные фильтры
│   ├── __init__.py
│   ├── has_text.py            # Фильтр сообщений с текстом
│   └── has_image.py           # Фильтр сообщений с изображениями
│
├── states/                    # FSM состояния
│   └── __init__.py            # Состояния для создания мемов
│
├── utils/                     # Утилиты
│   ├── __init__.py
│   ├── logger.py              # Настройка логирования
│   └── formatters.py          # Форматирование данных
│
└── storage/                   # Локальное хранилище
    └── favorites_storage.json # JSON база избранных мемов
```

## Установка и настройка

### Требования
- Python 3.10+
- pip (менеджер пакетов Python)
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))

### Шаги установки

1. **Клонирование проекта**
```bash
git clone <repository-url>
cd Anliiia-sem2-proj2
```

2. **Установка зависимостей**
```bash
pip install -r requirements.txt
```

3. **Настройка переменных окружения**

Создайте файл `.env` в корне проекта:
```env
BOT_TOKEN=your_bot_token_here
```

4. **Запуск бота**
```bash
python bot.py
```

### Зависимости
```
aiogram==3.13.1         # Асинхронная библиотека для Telegram Bot API
aiohttp==3.10.11        # HTTP клиент для асинхронных запросов
python-dotenv==1.1.0    # Загрузка переменных окружения
```

## Использование

### Базовые команды
1. **Начало работы**: отправьте `/start` боту
2. **Случайный котик**: используйте `/randomcat`
3. **Создание мема**: выберите `/newmeme` и следуйте инструкциям
4. **Управление избранным**: команда `/favorites`

### Создание мема
1. Выберите `/newmeme`
2. Выберите источник изображения (случайный кот или загрузите свое)
3. Введите верхний текст (или пропустите) - **только на английском языке**
4. Введите нижний текст (или пропустите) - **только на английском языке**
5. Подтвердите создание мема
6. Получите готовый мем с возможностью добавления в избранное

**Важно**: Текст мемов поддерживается только на английском языке из-за ограничений API Memegen.link.

### Работа с изображениями
- **Загрузка изображений**: просто отправьте фото боту
- **Автоматические предложения**: бот предложит создать мем или добавить в избранное
- **Поддержка форматов**: JPG, PNG, WebP

## Разработка

### Технический стек
- **aiogram 3** — современная асинхронная библиотека для Telegram
- **asyncio** — асинхронное программирование
- **aiohttp** — HTTP клиент для API запросов
- **JSON** — локальное хранилище данных
- **Logging** — система логирования

### Паттерны и принципы
- **Router-based architecture** — модульная маршрутизация
- **FSM (Finite State Machine)** — управление состояниями пользователя
- **Middleware pattern** — промежуточная обработка запросов
- **Filter pattern** — фильтрация входящих сообщений
- **MVC pattern** — разделение логики, данных и представления

### Расширение функционала

#### Добавление новых команд
1. Создайте обработчик в `routers/commands.py`
2. Зарегистрируйте роутер в `bot.py`
3. Добавьте описание в команду `/help`

#### Добавление новых фильтров
1. Создайте класс фильтра в `filters/`
2. Наследуйтесь от `BaseFilter`
3. Импортируйте в `filters/__init__.py`
4. Используйте в декораторах обработчиков

#### Интеграция новых API
1. Добавьте методы в `services/api_client.py`
2. Создайте соответствующие обработчики
3. Обновите конфигурацию в `config/settings.py`

## API интеграции

### The Cat API
- **Endpoint**: `https://api.thecatapi.com/v1/images/search`
- **Функция**: получение случайных изображений котов
- **Rate limit**: 1000 запросов/час (без ключа)

### Memegen.link API
- **Endpoint**: `https://api.memegen.link/images/custom`
- **Функция**: генерация мемов с пользовательским текстом
- **Формат**: `/{top_text}/{bottom_text}.jpg`
- **Ограничения**: Поддерживается только английский текст

## Отладка

### Логи
Все события сохраняются в `bot.log`:
```
[2024-06-08 15:30:25] Update: message, User ID: 123456789
[2024-06-08 15:30:25] Command: /start by user unknown (ID: 123456789)
[2024-06-08 15:30:30] Callback: random_cat by user unknown (ID: 123456789)
```

### Типичные проблемы
1. **Токен не работает**: проверьте `.env` файл
2. **API недоступно**: используйте `/test` для проверки
3. **Ошибки состояний**: перезапустите бота командой `/start`

## Производительность

### Оптимизации
- **Асинхронная обработка** всех запросов
- **Кэширование** изображений котов
- **Локальное хранилище** для избранного
- **Эффективная обработка** callback запросов

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте файл `.env` и добавьте токен бота:
```
BOT_TOKEN=your_bot_token_here
```

3. Запустите бота:
```bash
python bot.py
```

