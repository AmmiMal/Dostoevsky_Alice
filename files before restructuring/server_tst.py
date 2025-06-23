from flask import Flask, request
import logging
import json
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
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


def help(res):
    res['response']['text'] = ''
    return


def incomprehension_base(res):
    res['response'][
        'text'] = 'Не понимаю команды. Для продолжения диалога скажите: "Да", "Давай", "Дальше". Если хотите завершить, скажите "Хватит". Для вызова помощи, скажите команду "Помощь".'
    return


def handle_dialog(res, req):
    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['text'] = (
            f'Привет! Сегодня я предлагаю Вам окунуться в мир произведений Фёдора Михайловича Достоевского! '
            f'Я проведу Вас по местам, упоминающимся в произведениях великого классика! '
            f'Вы можете пройти маршрут как вместе со мной, так и виртуально. '
            f'Во время нашего путешествия вы всегда можете попросить инструкцию, сказав "Помощь". ')
        res['response']['buttons'] = [
            {'title': 'Да', 'hide': True},
            {'title': 'Давай', 'hide': True},
            {'title': 'Помощь', 'hide': True}
        ]
        return

    tokens = [token.lower() for token in req['request']['nlu']['tokens']]

    if any(token in ['хватит', 'стоп'] for token in tokens):
        res['response']['end_session'] = True
        res['response']['text'] = 'До свидания!'
        return

    if 'помощь' in tokens:
        res['response'][
            'text'] = 'Для продолжения диалога скажите: "Да", "Давай", "Дальше". Если хотите завершить, скажите "Хватит".'
        res['response']['buttons'] = [
            {'title': 'Да', 'hide': True},
            {'title': 'Давай', 'hide': True},
            {'title': 'Хватит', 'hide': True}
        ]
        return

    if req['request']['original_utterance'].lower() in ['да', 'дальше', 'давай', 'интересно', 'хорошо']:
        res['response'][
            'text'] = 'Прекрасно! Если Вы хотите попутешествовать по этим местам, я подготовила экскурсию по двум ключевым произведениям: «Преступление и наказание» и «Идиот»'
        res['response']['buttons'] = [
            {'title': 'Преступление и наказание', 'hide': True},
            {'title': 'Идиот', 'hide': True},
            {'title': 'Помощь', 'hide': True}
        ]
    else:
        incomprehension_base(res)
        return

    if 'преступление и наказание' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'Отличный выбор! Итак, начнём наше путешествие!'
        play_pr(res, req)
    elif 'идиот' in req['request']['original_utterance'].lower():
        play_pr(res, req)


def play_pr(res, req):
    name = req['request']['original_utterance']
    # Если вдруг стало скучно, скажи об этом ...
    res['response']['text'] = (f'Ты выбрал {name}.')
    if name == 'Преступление и наказание':
        res['response']['tts'] = (f'Это произведение автор задумал во время ссылки. \
        И, в+идя перемены в стране и обществе, принял решение о неабхадимости начать роман имено в тот момент.')
    if name == 'Идиот':
        res['response']['tts'] = (f'Идея произведения - изобразить вполне прекрасного человека.\
         Труднее этого, по-моему, быть ничего не может, особенно в наше время!')
    # как-то через 1 цикл реализовать маршрут для обоих произведений (создать что-то по типу json для каждого места и \
    # сделать количество итераций по его длине, в цикли же и обрабатывать запросы пользователя)


if __name__ == '__main__':
    app.run()
