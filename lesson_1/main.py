import os
from urllib.parse import urljoin

import requests
import telegram
from dotenv import load_dotenv
from requests.exceptions import Timeout

load_dotenv()


def devman_long_polling(token):
    """ Wait for new new reviews results."""

    url = 'https://dvmn.org/api/long_polling/'
    headers = {'Authorization': 'Token {}'.format(token)}
    params = {'timestamp': None}

    while True:
        try:
            response = requests.get(url, params=params, headers=headers, timeout=100)
            params['timestamp'] = response.json().get('timestamp_to_request')
            yield response.json()

        except Timeout:
            continue


def get_message_text_from_json(attempt_data):
    """Create text of message from attempt JSON data"""

    task_url = urljoin('https://dvmn.org/', attempt_data['lesson_url'])
    text = 'У вас проверили работу [«{}»]({}).\n\n'.format(attempt_data['lesson_title'], task_url)

    if attempt_data['is_negative']:
        text += 'К сожалению в работе нашлись ошибки.'
    else:
        text += 'Преподавателю все понравилось, можно приступать к следующему уроку!'

    return text


def send_message(bot, chat_id, message):
    """Send message from bot to user with chat_id"""
    bot.send_message(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)


def main():
    devman_token = os.environ.get('DEVMAN_TOKEN')
    bot_token = os.environ.get('BOT_TOKEN')
    author_chat_id = os.environ.get('AUTHOR_CHAT_ID')

    devman_bot = telegram.Bot(token=bot_token)

    for result in devman_long_polling(devman_token):
        for new_attempt in result.get('new_attempts', []):
            send_message(devman_bot, author_chat_id, get_message_text_from_json(new_attempt))


if __name__ == '__main__':
    main()
