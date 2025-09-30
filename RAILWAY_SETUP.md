# Railway Deployment Guide

## Быстрая инструкция по деплою в Railway

### Шаг 1: Подготовка GitHub репозитория

1. Убедитесь что у вас есть GitHub аккаунт
2. Создайте новый репозиторий на GitHub (можно private или public)
3. В текущей директории выполните:

```bash
git init
git add .
git commit -m "Initial commit: Unified Mocks Service"
git branch -M main
git remote add origin https://github.com/ваш-юзернейм/название-репозитория.git
git push -u origin main
```

### Шаг 2: Настройка Railway

1. Зайдите на [railway.app](https://railway.app)
2. Нажмите "Start a New Project"
3. Выберите "Deploy from GitHub repo"
4. Авторизуйте Railway для доступа к вашему GitHub (если еще не сделано)
5. Выберите ваш репозиторий

### Шаг 3: Настройка переменных окружения

После создания проекта в Railway:

1. Откройте ваш проект
2. Перейдите в раздел "Variables"
3. Добавьте следующие переменные:

```
TELEGRAM_BOT_TOKEN=8331243138:AAHaZkZVyMBdeCvjYRvDo9vIgDG4Ga5Uw38
TELEGRAM_ADMIN_IDS=ваш_telegram_user_id
TELEGRAM_CHAT_ID=ваш_chat_id
```

#### Как получить TELEGRAM_ADMIN_IDS:
1. Напишите боту [@userinfobot](https://t.me/userinfobot)
2. Он отправит вам ваш ID (например: 123456789)
3. Если админов несколько, разделите запятой: `123456789,987654321`

#### Как получить TELEGRAM_CHAT_ID:
1. Создайте группу в Telegram
2. Добавьте вашего бота в эту группу (используя @имя_бота)
3. Добавьте бота [@getidsbot](https://t.me/getidsbot) в эту же группу
4. Он отправит Chat ID (например: -100123456789)
5. Удалите @getidsbot из группы (он больше не нужен)

### Шаг 4: Деплой

Railway автоматически:
- Обнаружит Python проект
- Установит зависимости из `requirements.txt`
- Запустит сервис используя команду из `railway.json`

Процесс деплоя займет 2-3 минуты.

### Шаг 5: Получение URL

После успешного деплоя:

1. В Railway перейдите в "Settings" → "Networking"
2. Нажмите "Generate Domain"
3. Railway выдаст вам публичный URL (например: `https://your-project.up.railway.app`)

### Шаг 6: Проверка работы

1. Откройте URL в браузере - вы должны увидеть JSON с информацией о сервисе
2. Добавьте `/docs` к URL для доступа к Swagger документации
3. Напишите `/start` вашему боту в Telegram - он должен ответить

## Автоматическое обновление

После первой настройки каждый `git push` в ветку `main` будет автоматически:
1. Триггерить новый деплой в Railway
2. Перезапускать сервис с новым кодом

## Логи и мониторинг

В Railway:
- Вкладка "Deployments" - история деплоев
- Вкладка "Observability" - логи в реальном времени
- Вкладка "Metrics" - использование ресурсов

## Тестирование API

После деплоя вы можете тестировать API:

```bash
# Health check
curl https://your-project.up.railway.app/health

# Status
curl https://your-project.up.railway.app/mocks/config

# Payment test
curl -X POST https://your-project.up.railway.app/mocks/payment \
  -H "Content-Type: application/json" \
  -d '{
    "kiosk_id": "kiosk_001",
    "order_id": 9999995,
    "sum": 57000
  }'
```

## Управление через Telegram

После настройки всех переменных окружения, вы можете управлять сервисом через Telegram:

- `/status` - текущий статус всех сервисов
- `/config` - изменить настройки сервисов
- `/logs` - посмотреть последние логи

## Troubleshooting

### Бот не отвечает
- Проверьте `TELEGRAM_BOT_TOKEN` в Variables
- Проверьте что ваш ID есть в `TELEGRAM_ADMIN_IDS`
- Посмотрите логи в Railway Observability

### Сервис не запускается
- Проверьте логи деплоя в Railway
- Убедитесь что все зависимости установлены
- Проверьте что переменная `PORT` не задана (Railway устанавливает её автоматически)

### Ошибка при деплое
- Убедитесь что `requirements.txt` корректный
- Проверьте что `railway.json` существует
- Посмотрите детальные логи билда в Railway

## Стоимость

Railway предоставляет:
- $5 бесплатных кредитов каждый месяц
- Этого хватит для круглосуточной работы небольшого сервиса
- Дополнительные кредиты можно купить при необходимости
