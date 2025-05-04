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
    res['response']['text'] = 'Не понимаю команды. Для продолжения диалога скажите: "Да", "Давай", "Дальше". Если хотите завершить, скажите "Хватит". Для вызова помощи, скажите команду "Помощь".'
    return


def handle_dialog(res, req):
    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['text'] = (f'Привет! Сегодня я предлагаю Вам окунуться в мир произведений Фёдора Михайловича Достоевского! '
                                   f'Я проведу Вас по местам, упоминающимся в произведениях великого классика! '
                                   f'Вы можете пройти маршрут как вместе со мной, так и виртуально. '
                                   f'Во время нашего путешествия вы всегда можете попросить инструкцию, сказав "Помощь". ')
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
    if 'Помощь' in req['request']['nlu']['tokens']:
        res['response']['text'] = 'Для продолжения диалога скажите: "Да", "Давай", "Дальше". Если хотите завершить, скажите "Хватит".'

    if req['request']['nlu']['tokens'].lower() in ['хватит', 'стоп']:
        exit()
        # res['response']['text'] = 'Для продолжения'

    if req['request']['original_utterance'].lower() in [
        'да', 'дальше',
        'давай',
        'интересно',
        'хорошо'
    ]:
        res['response']['text'] = 'Прекрасно! Если Вы хотите попутешествовать по этим местам, то я подготовила для Вас экскурсию по двум ключевым произведениям: «Преступление и наказание» и «Идиот»'
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
    else:
        incomprehension_base(res)

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
    elif 'Преступление и наказание' in req['request']['original_utterance']:
        res['response']['text'] = 'Отличный выбор! Итак, начнем наше путешествие!'
        play_pr(res, req)
    elif 'Идиот' in req['request']['original_utterance']:
        play_pr(res, req)
    else:
        incomprehension_base(res)


def play_pr(res, req):
    name = req['request']['original_utterance']
    # Если вдруг стало скучно, скажи об этом ...
    res['response']['text'] = (f'Ты выбрал {name}.')
    if name == 'Преступление и наказание':
        res['response']['tts'] = (f'Это произвид+ение автор зад+умал во время ссылки. \
        И, в+идя перемены в стране и обществе, пр+инял решение о неабхадимости начать роман имено в тот момент.')
    if name == 'Идиот':
        res['response']['tts'] = (f'Идея произведения - изобразить вполне прекрасного человека.\
         Труднее этого, по-моему, быть ничего не может, особенно в наше время!')
    # как-то через 1 цикл реализовать маршрут для обоих произведений (создать что-то по типу json для каждого места и \
    # сделать количество итераций по его длине, в цикли же и обрабатывать запросы пользователя)


    # user_id = req['session']['user_id']
    # attempt = sessionStorage[user_id]['attempt']
    # if attempt == 1:
    #     # если попытка первая, то случайным образом выбираем город для гадания
    #     city = random.choice(list(cities))
    #     # выбираем его до тех пор пока не выбираем город, которого нет в sessionStorage[user_id]['guessed_cities']
    #     while city in sessionStorage[user_id]['guessed_cities']:
    #         city = random.choice(list(cities))
    #     # записываем город в информацию о пользователе
    #     sessionStorage[user_id]['city'] = city
    #     # добавляем в ответ картинку
    #     res['response']['card'] = {}
    #     res['response']['card']['type'] = 'BigImage'
    #     res['response']['card']['title'] = 'Что это за город?'
    #     res['response']['card']['image_id'] = cities[city][attempt - 1]
    #     res['response']['text'] = 'Тогда сыграем!'
    #     res['response']['buttons'] = [
    #         {
    #             'title': 'Помощь',
    #             'hide': True
    #         }]
    # else:
    #     # сюда попадаем, если попытка отгадать не первая
    #     city = sessionStorage[user_id]['city']
    #     if 'помощь' in req['request']['nlu']['tokens']:
    #         res['response']['text'] = 'Введи название города.'
    #         res['response']['buttons'] = [
    #             {
    #                 'title': 'Помощь',
    #                 'hide': True
    #             }
    #         ]
    #         return
    #     # проверяем есть ли правильный ответ в сообщение
    #     if get_city(req) == city:
    #         # если да, то добавляем город к sessionStorage[user_id]['guessed_cities'] и
    #         # отправляем пользователя на второй круг. Обратите внимание на этот шаг на схеме.
    #         res['response']['text'] = 'Правильно! Сыграем ещё?'
    #         sessionStorage[user_id]['guessed_cities'].append(city)
    #         sessionStorage[user_id]['game_started'] = False
    #         res['response']['buttons'] = [
    #             {
    #                 'title': 'Да',
    #                 'hide': True
    #             },
    #             {
    #                 'title': 'Нет',
    #                 'hide': True
    #             },
    #             {
    #                 'title': 'Помощь',
    #                 'hide': True
    #             }
    #         ]
    #         return
    #     else:
    #         # если нет
    #         if attempt == 3:
    #             если попытка третья, то значит, что все картинки мы показали.
    #             В этом случае говорим ответ пользователю,
    #             добавляем город к sessionStorage[user_id]['guessed_cities'] и отправляем его на второй круг.
    #             Обратите внимание на этот шаг на схеме.
    #             res['response']['text'] = f'Вы пытались. Это {city.title()}. Сыграем ещё?'
    #             sessionStorage[user_id]['game_started'] = False
    #             sessionStorage[user_id]['guessed_cities'].append(city)
    #             return
    #         else:
    #              иначе показываем следующую картинку
    #             res['response']['card'] = {}
    #             res['response']['card']['type'] = 'BigImage'
    #             res['response']['card']['title'] = 'Неправильно. Вот тебе дополнительное фото'
    #             res['response']['card']['image_id'] = cities[city][attempt - 1]
    #             res['response']['text'] = 'А вот и не угадал!'
    # увеличиваем номер попытки доля следующего шага
    # sessionStorage[user_id]['attempt'] += 1


def play_id(res, req):
    user_id = req['session']['user_id']
    attempt = sessionStorage[user_id]['attempt']
    if attempt == 1:
        # если попытка первая, то случайным образом выбираем город для гадания
        city = random.choice(list(cities))
        # выбираем его до тех пор пока не выбираем город, которого нет в sessionStorage[user_id]['guessed_cities']
        while city in sessionStorage[user_id]['guessed_cities']:
            city = random.choice(list(cities))
        # записываем город в информацию о пользователе
        sessionStorage[user_id]['city'] = city
        # добавляем в ответ картинку
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = 'Что это за город?'
        res['response']['card']['image_id'] = cities[city][attempt - 1]
        res['response']['text'] = 'Тогда сыграем!'
        res['response']['buttons'] = [
            {
                'title': 'Помощь',
                'hide': True
            }]
    else:
        # сюда попадаем, если попытка отгадать не первая
        city = sessionStorage[user_id]['city']
        if 'помощь' in req['request']['nlu']['tokens']:
            res['response']['text'] = 'Введи название города.'
            res['response']['buttons'] = [
                {
                    'title': 'Помощь',
                    'hide': True
                }
            ]
            return
        # проверяем есть ли правильный ответ в сообщение
        if get_city(req) == city:
            # если да, то добавляем город к sessionStorage[user_id]['guessed_cities'] и
            # отправляем пользователя на второй круг. Обратите внимание на этот шаг на схеме.
            res['response']['text'] = 'Правильно! Сыграем ещё?'
            sessionStorage[user_id]['guessed_cities'].append(city)
            sessionStorage[user_id]['game_started'] = False
            res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                },
                {
                    'title': 'Помощь',
                    'hide': True
                }
            ]
            return
        else:
            # если нет
            if attempt == 3:
                # если попытка третья, то значит, что все картинки мы показали.
                # В этом случае говорим ответ пользователю,
                # добавляем город к sessionStorage[user_id]['guessed_cities'] и отправляем его на второй круг.
                # Обратите внимание на этот шаг на схеме.
                res['response']['text'] = f'Вы пытались. Это {city.title()}. Сыграем ещё?'
                sessionStorage[user_id]['game_started'] = False
                sessionStorage[user_id]['guessed_cities'].append(city)
                return
            else:
                # иначе показываем следующую картинку
                res['response']['card'] = {}
                res['response']['card']['type'] = 'BigImage'
                res['response']['card']['title'] = 'Неправильно. Вот тебе дополнительное фото'
                res['response']['card']['image_id'] = cities[city][attempt - 1]
                res['response']['text'] = 'А вот и не угадал!'
    # увеличиваем номер попытки доля следующего шага
    sessionStorage[user_id]['attempt'] += 1


def get_city(req):
    # перебираем именованные сущности
    for entity in req['request']['nlu']['entities']:
        # если тип YANDEX.GEO, то пытаемся получить город(city), если нет, то возвращаем None
        if entity['type'] == 'YANDEX.GEO':
            # возвращаем None, если не нашли сущности с типом YANDEX.GEO
            return entity['value'].get('city', None)


def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name', то возвращаем её значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()
