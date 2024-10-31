# Проект 3 экстерната Python Хамидуллин Рустам
Результат работы - запускаемый на локальном хосте сайт, введя на котором широту и долготу начальной и 
конечной точки маршрута, можно получить информацию о прогнозе погоды на 3 или 5 дней.

# Перед запуском необходимо:
1. Установить в виртуальном окружении библиотеки, используемые в проекте (описаны в [requirements.txt](requirements.txt)).
2. В файле [initialize.py](app.py) заменить исходный API-ключ на собственный.

## Для запуска веб-страницы
1. В консоли виртуального окружения ввести ```python main.py```
2. Приложение захостится на localhost. его можно открывать в браузере и тестировать!

## Для запуска тг-бота
1. Запустить файл [bot](tg_bot/bot.py)
2. в телеграме по тегу @xilserweather_bot можно запустить бота и тестировать! 

## Содержимое файлов
1. [API_requests](API_requests.py) - реализация запросов к AccuWeatherAPI для получения информации о погоде по координатам точки
2. [bot](tg_bot/bot.py) - тг бот, действующий на апишке из [API_requests](API_requests.py), который реализует тот же функционал что и веб-страница.
3. [errors](errors.py) - кастомные ошибки, используемые при возникании проблем с запросами и API-ключом
4. [initialize](initialize.py) - константы, используемые в коде
5. [main](main.py) - файл, содержащий Dash-callback'и

