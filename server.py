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


class DostoevskyLocationsIterator:
    def __init__(self, locations_data, include_map_links=False):
        self.locations_data = locations_data
        self.include_map_links = include_map_links
        self.current_index = 1  # Начинаем с location_1
        self.max_index = len(locations_data)

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_index > self.max_index:
            raise StopIteration
        with open(self.locations_data, 'r', encoding='utf-8') as file:
            data = json.load(file)

        location_key = f"location_{self.current_index}"
        location = data.get(location_key)

        if not location:
            raise StopIteration

        response = {
            'real_name': location['real_name'],
            'plot': location['plot'],
            'photo_path': location['photo_path']
        }

        # Добавляем дополнительную информацию, если она есть
        if 'exterior_description' in location:
            response['exterior_description'] = location['exterior_description']

        # Добавляем ссылку на карты по желанию пользователя
        if self.include_map_links:
            response['yandex_maps_link'] = location['yandex_maps_link']

        self.current_index += 1
        return response


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


def incomprehension_base(res, type):
    if type == 'continue':
        res['response']['text'] = 'Не понимаю команды. Для продолжения диалога скажите: "Да", "Давай", "Дальше". Если хотите завершить, скажите "Хватит". Для вызова помощи, скажите команду "Помощь".'
        return
    elif type == 'choise':
        res['response']['text'] = 'Не понимаю команды. Для продолжения диалога скажите или нажмите на кнопку: "Да" или "Нет". Если хотите завершить, скажите "Хватит". Для вызова помощи, скажите команду "Помощь".'
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


def handle_dialog(res, req):
    print(1)
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


    if any(token in ['хватит', 'стоп'] for token in [token.lower() for token in req['request']['nlu']['tokens']]):
        res['response']['end_session'] = True
        res['response']['text'] = 'До свидания!'
        return

    if 'помощь' in [token.lower() for token in req['request']['nlu']['tokens']]:
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
    # else:
    #     incomprehension_base(res, '')
    #     return
    print(2)
    if 'преступление и наказание' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'Отличный выбор! Итак, начнём наше путешествие!'
        play_pr(res, req)
    elif 'идиот' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'Отличный выбор! Итак, начнём наше путешествие!'
        play_pr(res, req)
    elif 'Помощь' in req['request']['original_utterance']:
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
        res['response']['text'] = 'Отличный выбор! Итак, начнем наше путешествие!'
        play_pr(res, req)
    else:
        incomprehension_base(res, 'continue')


def play_pr(res, req):
    name = req['request']['original_utterance']
    print(name)
    locations_data = ''
    links_need = 'Для комфортного путешествия, пожалуйста, сообщите будут ли необходимы ссылки на локации в Яндекс Картах.'
    # # Если вдруг стало скучно, скажи об этом ...
    if name == 'Преступление и наказание':
        res['response']['text'] = (f'Ты выбрал {name}.\n {links_need}')
        res['response']['tts'] = (f'Это произвид+ение автор зад+умал во время ссылки. \
        И, в+идя перемены в стране и обществе, пр+инял решение о неабхадимости начать роман имено в тот момент.')
    if name == 'Идиот':
        res['response']['text'] = (f'Ты выбрал {name}.\n {links_need}')
        res['response']['tts'] = (f'Идея произведения - изобразить вполне прекрасного человека.\
         Труднее этого, по-моему, быть ничего не может, особенно в наше время!')
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
    if 'Помощь' in req['request']['nlu']['tokens']:
        res['response'][
            'text'] = 'Для продолжения диалога скажите: "Да" или "Нет". Если хотите завершить, скажите "Хватит".'
    elif any(word in req['request']['nlu']['tokens'] for word in['хватит', 'стоп']):
        exit()
    else:
        incomprehension_base(res, '')

    if name == 'Преступление и наказание':
        locations_data = 'Crime_and_Punishment.json'
    if name == 'Идиот':
        locations_data = 'Idiot.json'
    locations_iterator = DostoevskyLocationsIterator(locations_data)
    for location in locations_iterator:
        # res['response']['card'] = {}
        # res['response']['card']['type'] = 'BigImage'
        # res['response']['card']['title'] = location['real_name']
        # res['response']['card']['image_id'] = location['photo_path']
        res['response']['text'] = location['plot']
        res['response']['buttons'] = [
            {
                'title': 'Помощь',
                'hide': True
            }]
    #
    # # Создаем итератор со ссылками на карты
    # locations_iterator_with_maps = DostoevskyLocationsIterator(locations_data, include_map_links=True)
    # for location in locations_iterator_with_maps:
    #     # res['response']['card'] = {}
    #     # res['response']['card']['type'] = 'BigImage'
    #     # res['response']['card']['title'] = location['real_name']
    #     # res['response']['card']['image_id'] = location['photo_path']
    #     res['response']['text'] = location['plot']
    #     res['response']['buttons'] = [
    #         {
    #             'title': 'Помощь',
    #             'hide': True
    #         }, {
    #             'title': 'Ссылка на локацию',
    #             'url': location['yandex_maps_link'],
    #             'payload': {},
    #             "hide": True
    #         }]



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
