import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import schedule
import time
from telegram import Bot

# Настройки для Telegram
TELEGRAM_TOKEN = '7713528429:AAFOHgwcRkHoihZRLl_a7FLknA7ifjYXLqA'  # Ваш токен Telegram-бота
CHAT_ID = '@smolotka14'  # ID вашего канала

# Часовой пояс Якутска
yakutsk_tz = pytz.timezone('Asia/Yakutsk')


# Функции парсинга для каждого кинотеатра
def parse_cinema_asiakino():
    url = 'http://asiakino.ru/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    films = []
    for film in soup.select('.film'):
        title = film.select_one('.film-title').text
        tags = [tag.text for tag in film.select('.film-genre')]
        showtimes = [showtime.text for showtime in film.select('.showtime')]
        films.append({
            'title': title,
            'tags': tags,
            'showtimes': showtimes,
            'hall': None,
            'price': None
        })
    return 'Кинотеатр "Азия"', films


def parse_cinema_lena():
    url = 'https://cinemalena.com/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    films = []
    for film in soup.select('.film-item'):
        title = film.select_one('.film-title').text
        tags = [tag.text for tag in film.select('.film-tags span')]
        showtimes = [showtime.text for showtime in film.select('.film-showtimes span')]
        price = film.select_one('.film-price').text if film.select_one('.film-price') else None
        hall = film.select_one('.film-hall').text if film.select_one('.film-hall') else None
        films.append({
            'title': title,
            'tags': tags,
            'showtimes': showtimes,
            'hall': hall,
            'price': price
        })
    return 'Кинотеатр "Лена"', films


def parse_cinema_center():
    url = 'https://cinema-center.ru/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    films = []
    for film in soup.select('.movie-item'):
        title = film.select_one('.movie-title').text
        tags = [tag.text for tag in film.select('.movie-genres span')]
        showtimes = [showtime.text for showtime in film.select('.movie-showtimes span')]
        price = film.select_one('.movie-price').text if film.select_one('.movie-price') else None
        hall = film.select_one('.movie-hall').text if film.select_one('.movie-hall') else None
        films.append({
            'title': title,
            'tags': tags,
            'showtimes': showtimes,
            'hall': hall,
            'price': price
        })
    return 'Кинотеатр "Синема-Центр"', films


def parse_cinema_emeyan():
    url = 'https://emeyan.ru/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    films = []
    for film in soup.select('.event'):
        title = film.select_one('.event-title').text
        tags = [tag.text for tag in film.select('.event-tags span')]
        showtimes = [showtime.text for showtime in film.select('.event-showtimes span')]
        price = film.select_one('.event-price').text if film.select_one('.event-price') else None
        hall = film.select_one('.event-hall').text if film.select_one('.event-hall') else None
        films.append({
            'title': title,
            'tags': tags,
            'showtimes': showtimes,
            'hall': hall,
            'price': price
        })
    return 'Кинотеатр "Емеян"', films


def parse_cinema_aviator():
    url = 'https://kinowidget.kinoplan.ru/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    films = []
    for film in soup.select('.session-item'):
        title = film.select_one('.session-title').text
        tags = [tag.text for tag in film.select('.session-genres span')]
        showtimes = [showtime.text for showtime in film.select('.session-times span')]
        price = film.select_one('.session-price').text if film.select_one('.session-price') else None
        hall = film.select_one('.session-hall').text if film.select_one('.session-hall') else None
        films.append({
            'title': title,
            'tags': tags,
            'showtimes': showtimes,
            'hall': hall,
            'price': price
        })
    return 'Кинотеатр "Авиатор"', films


# Отправка сообщений в Telegram
def send_message(bot, text):
    bot.send_message(chat_id=CHAT_ID, text=text)


# Формируем сообщение для Telegram
def prepare_message(cinema_name, films):
    today = datetime.now(yakutsk_tz).strftime("%d.%m.%Y")
    message = f"Расписание на {today} в {cinema_name}:\n\n"
    for film in films:
        message += f"🎬 {film['title']}\n"
        message += f"Теги: {', '.join(film['tags'])}\n"
        message += f"Время сеансов: {', '.join(film['showtimes'])}\n"
        if film.get('price'):
            message += f"Цена: {film['price']}\n"
        if film.get('hall'):
            message += f"Зал: {film['hall']}\n"
        message += "\n"
    return message


# Главная функция, которая парсит данные со всех кинотеатров и отправляет сообщения
def main():
    bot = Bot(token=TELEGRAM_TOKEN)

    # Парсим данные с каждого кинотеатра
    cinemas = [
        parse_cinema_asiakino,
        parse_cinema_lena,
        parse_cinema_center,
        parse_cinema_emeyan,
        parse_cinema_aviator
    ]

    for cinema_parser in cinemas:
        cinema_name, films = cinema_parser()
        message = prepare_message(cinema_name, films)
        send_message(bot, message)


# Планировщик задач (ежедневно в 8:00 по якутскому времени)
def job():
    now = datetime.now(yakutsk_tz)
    if now.hour == 8:
        main()


# Настройка расписания
schedule.every().day.at("08:00").do(job)

# Запуск цикла выполнения задач
if _name_ == "_main_":
    while True:
        schedule.run_pending()
        time.sleep(60)