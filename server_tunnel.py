# Используем https://serveo.net/ для подключения нашего навыка через туннель в интернет
# для тестирования в своей ветке и удаленно на своем устройстве

from flask import Flask, request
import logging
import json
import random

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

sessionStorage = {}

@app.route('/post', methods=['POST']) # не забываем указывать в ссылке навыка путь + \post

def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['text'] = (f'Приятно познакомиться. Сегодня я предлагаю тебе окунуться в мир произведений '
                                   f'Фёдора Михайловича Достоевского. Начнем мы с тобой с произведения "Преступление и наказание" ')
        res['response']['buttons'] = [
            {
                'title': 'Да',
                'hide': True
            },
            {
                'title': 'Давай',
                'hide': True
            },
            {
                'title': 'Помощь',
                'hide': True
            }
        ]
    if 'помощь' in req['request']['nlu']['tokens'] and req['session']['new']:
        help_base(res)


    if req['request']['original_utterance'].lower() in [
        'да',
        'давай',
        'интересно',
        'хорошо'
    ]:
        res['response']['text'] = 'Прекрасно! Если ты хочешь попутешествовать по этим местам, то я подготовила для тебя экскурсию по двум ключевым произведениям: «Преступление и наказание» и «Идиот»'
        res['response']['buttons'] = [
            {
                'title': 'Преступление и наказание',
                'hide': True
            },
            {
                'title': 'Идиот',
                'hide': True
            },
            {
                'title': 'Помощь',
                'hide': True
            }
        ]
    if 'Помощь' in req['request']['original_utterance']:
        print(1)
        res['response']['text'] = 'Выберете произведение.'
        res['response']['buttons'] = [
            {
                'title': 'Преступление и наказание',
                'hide': True
            },
            {
                'title': 'Идиот',
                'hide': True
            }]
        return
    if 'Преступление и наказание' in req['request']['original_utterance']:
        res['response']['text'] = 'Отличный выбор! Итак, начнем наше путешествие!'
        play_pr(res, req)
    if 'Идиот' in req['request']['original_utterance']:
        play_pr(res, req)


def help_base(res):
    res['response']['text'] = 'бла бла'
    print(0)


def play_pr(res, req):
    res['response']['text'] = f'Отличный выбор! Итак, начнем наше путешествие! Ты выбрал Преступление и наказание. Это произведение автор задумал во время ссылки. \
    И, видя перемены в стране и обществе, принял решение о необходимости начать роман именно в тот момент.'

if __name__ == '__main__':
    app.run()
