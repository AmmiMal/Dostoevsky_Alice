# app.py
from flask import Flask, request, jsonify
import logging
import threading

from scene import Scene, HelpContextScene
from handlers import ExitHandler, HelpHandler, WaitForNextHandler, NextSceneHandler
from utils import load_scene_from_file, format_buttons
from config import DEFAULT_SCENE, END_SCENE, SCENES_DIR, HELP_SCENE

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

sessionStorage = {}
session_lock = threading.Lock()


def load_scene(scene_name):
    resource = load_scene_from_file(scene_name)
    handlers = get_handlers(lambda name: load_scene(name))
    return Scene(resource, handlers)


def get_help_replicas():
    help_data = load_scene_from_file(HELP_SCENE)
    return help_data["replics"]


def get_handlers(load_scene_func):
    exit_handler = ExitHandler()
    help_handler = HelpHandler(get_help_replicas, successor=None)
    next_scene_handler = NextSceneHandler(load_scene_func, successor=None)
    wait_next_handler = WaitForNextHandler(successor=None)

    exit_handler._successor = help_handler
    help_handler._successor = next_scene_handler
    next_scene_handler._successor = wait_next_handler
    wait_next_handler._successor = None

    return [exit_handler]


@app.route('/post', methods=['POST'])
def main():
    req = request.json
    session_id = req['session']['session_id']
    user_input = req['request'].get('original_utterance', '').lower()

    response = {
        'session': req['session'],
        'version': req['version'],
        'response': {
            'end_session': False,
            'text': '',
            'buttons': []
        }
    }

    with session_lock:
        if req['session']['new']:
            sessionStorage[session_id] = load_scene(DEFAULT_SCENE)
            current_scene = sessionStorage[session_id]
            replica = current_scene.get_next_replica()
            if replica:
                text = replica.get('text', '')
                buttons_data = replica.get('buttons', [])
                buttons_scene = current_scene.get_scene_buttons()

                all_buttons = buttons_data + buttons_scene

                response['response']['text'] = text
                response['response']['buttons'] = format_buttons(all_buttons)

            return jsonify(response)

        current_scene = sessionStorage.get(session_id)
        if not current_scene:
            response['response']['text'] = "Произошла ошибка."
            return jsonify(response)

        next_scene = current_scene.handle_input(user_input)
        if next_scene == 'Exit':
            response['response']['end_session'] = True
            response['response']['text'] = "До свидания!"
            return jsonify(response)

        if next_scene.is_done():
            next_scene_name = next(iter(next_scene.get_next_scenes().values()), END_SCENE)
            next_scene = load_scene(next_scene_name)

        replica = next_scene.get_next_replica()
        if replica:
            text = replica.get('text', '')
            card = replica.get('card', {})
            buttons_data = replica.get('buttons', [])
            buttons_scene = next_scene.get_scene_buttons()

            all_buttons = buttons_data + buttons_scene

            response['response']['text'] = text
            response['response']['buttons'] = format_buttons(all_buttons)

            if card != {}:
                response['response']['card'] = {}
                response['response']['card']['type'] = card['type']
                response['response']['card']['title'] = card['title']
                response['response']['card']['image_id'] = card['image_id']
                response['response']['card']['button'] = card['button']
        else:
            response['response']['text'] = "Это конец диалога."

        sessionStorage[session_id] = next_scene

    return jsonify(response)


if __name__ == "__main__":
    app.run()
