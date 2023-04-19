import logging
import os
import sys
from http import HTTPStatus
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

current_timestamp = 1681707645
timestamp = 1681707645


def check_tokens():
    """Проверяет доступность переменных окружения."""
    TOKEN = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
    }
    for name, token in TOKEN.items():
        if token is None:
            logging.warning(f'Переменной {name} нету)')
            sys.exit()


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        logging.info('Начало отправки')
        message = bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
    except telegram.TelegramError as error:
        logging.error(f'Сообщение отправлено {error}')
    else:
        logging.debug('Сообщение отправлено')


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT, headers=headers, params=params)
        logging.info('Запрос отправлен.')
        if response.status_code != HTTPStatus.OK:
            raise ConnectionError('Нету соеденения с сервером.')
        if not isinstance(response.json(), dict):
            raise TypeError('Не словарь')
        else:
            logging.info('Ответ от api ---- 200')
            return response.json()
    except Exception as error:
        raise Exception(f'Ошибка {error}')


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    logging.debug('Начало проверки')
    if not isinstance(response, dict):
        raise TypeError('Ошибка в ответе Api')
    if 'homeworks' not in response or 'current_date' not in response:
        raise TypeError('Пустой ответ')
    homework = response.get('homeworks')
    if not isinstance(homework, list):
        raise TypeError('Не являтся списком')


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус."""
    if 'homework_name' not in homework:
        raise KeyError('Ошибка в получении имени')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_VERDICTS:
        raise ValueError('Такого статуса в я нету')
    homework_name = homework_name
    verdict = HOMEWORK_VERDICTS[homework_status]
    return(f'Изменился статус проверки работы "{homework_name}". {verdict}')


def main():
    """Основная логика работы бота."""
    logging.debug('Бот работает')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    current_report = {}
    prev_report = {}
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)[0]
            if homework:
                message = parse_status(homework)
                current_report[
                    response.get('homework_name')] = response.get('status')
                if current_report != prev_report:
                    send_message(bot, message)
                    prev_report = current_report.copy()
                    current_report[
                        response.get('homework_name')] = response.get('status')
                else:
                    logging.debug('Статус не поменялся')
        except Exception as error:
            message = f'Ошибка в работе {error}'
            logging.error(message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s, %(levelname)s, %(message)s'
                        )
    main()
