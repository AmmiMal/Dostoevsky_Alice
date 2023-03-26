from flask import Flask, request
import logging
import json
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

cities = {
    'москва': ['997614/494dcfc652df991f14f1', '213044/8fce7841e115b5e23617'],
    'нью-йорк': ['1540737/cfc2650a7b5b06c7acfc', '1540737/ad3179678eca46c1bc10'],
    'париж': ["997614/b8f711c01dfbe8e6e7ae", '997614/fd5b178491d06d160ff9']
}

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


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if 'помощь' in req['request']['nlu']['tokens']:
        res['response']['text'] = 'бла бла'
        res['response']['buttons'] = [
            {
                'title': 'Помощь',
                'hide': True
            }
        ]
        return


    if req['session']['new']:
        res['response']['text'] = f'Приятно познакомиться. Сегодня я предлагаю тебе окунуться в мир произведений Фёдора Михайловича Достоевского?'
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
    if req['request']['original_utterance'].lower() in [
        'да',
        'давай',
        'интересно',
        'хорошо'
    ]:
        res['response']['text'] = 'Прекрасно! Если ты хочешь попутешествовать по этим местам, то я подготовила для тебя экскурсию по двум ключевым произведениям: «Преступление и наказание» и «Идиот»'
        # if len(sessionStorage[user_id]['guessed_cities']) == 3:
        #     # если все три города отгаданы, то заканчиваем игру
        #     res['response']['text'] = 'Ты отгадал все города!'
        #     res['end_session'] = True
        # else:
        #     # если есть неотгаданные города, то продолжаем игру
        #     sessionStorage[user_id]['game_started'] = True
        #     # номер попытки, чтобы показывать фото по порядку
        #     sessionStorage[user_id]['attempt'] = 1
        #     # функция, которая выбирает город для игры и показывает фото
        #     play_game(res, req)
    elif 'помощь' in req['request']['nlu']['tokens']:
        res['response']['text'] = 'Введи название города.'
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
    # else:
    #     res['response']['text'] = ' Извините, не поняла ответа.'
    #     res['response']['buttons'] = [
    #         {
    #             'title': 'Давай',
    #             'hide': True
    #         },
    #         {
    #             'title': 'Давай',
    #             'hide': True
    #         },
    #         {
    #             'title': 'Помощь',
    #             'hide': True
    #         }
    #     ]


def play_game(res, req):
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
