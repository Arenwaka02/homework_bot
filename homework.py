import logging
import os
import sys
from datetime import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv
from telegram import Bot

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
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
    except telegram.TelegramError as error:
        logging.error(f'Сообщение отправлено {error}')


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        response = requests.get(
            ENDPOINT, headers=headers, params=payload)
        logging.info('Запрос отправлен.')
        if response.status_code != 200:
            report = ('Проблема с API')
            logging.error(report)
    except Exception as error:
        raise Exception(f'Ошибка {error}')
    if response.status_code == HTTPStatus.OK:
        logging.info('Ответ получен.')
        return response.json()
    elif response.status_code == HTTPStatus.NOT_FOUND:
        logging.info('Ответ ne получен.')
    


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    logging.debug('Начало проверки')


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус этой работы."""
    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    logging.debug('Бот работает')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = 1681707645 # Unix Timestamp.
    current_report = {
        'name': '',
        'output': ''
    }
    prev_report = current_report.copy()
    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response.get(
                'current_data', current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                homework = homeworks[0]
                current_report['name'] = homework.get('homework_name')
                current_report['output'] = homework.get('status')
            else:
                current_report['output'] = 'НОВЫЙ РАБОТ НЕТ.'
            if current_report != prev_report:
                message = f' {current_report["name"]}, {current_report["output"]}'
                send_message(bot, message)
                prev_report = current_report.copy()
            else:
                logging.debug('Статус не изменился')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            current_report['output'] = message
            logging.error(message)
            if current_report != prev_report:
                message = f' {current_report["name"]}, {current_report["output"]}'
                send_message(bot, message)
                prev_report = current_report.copy()
        finally:
            time.sleep(RETRY_PERIOD)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s, %(levelname)s, %(message)s'
                        )
    main()
