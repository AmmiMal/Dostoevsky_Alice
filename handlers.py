# handlers.py
import re, random
from utils import load_scene_from_file


class Handler:
    def __init__(self, successor=None):
        self._successor = successor

    def handle(self, user_input, scene):
        if self._successor:
            return self._successor.handle(user_input, scene)
        return scene


class ExitHandler(Handler):
    def handle(self, user_input, scene):
        if re.search(r"(хватит|стоп|выход|пока|завершить)", user_input):
            return 'Exit'
        return super().handle(user_input, scene)


# handlers.py
class HelpHandler(Handler):
    def __init__(self, global_help_text, successor=None):
        super().__init__(successor)
        self.global_help_text = global_help_text

    def handle(self, user_input, scene):
        if re.search(r"(помощь|помог|что делать)", user_input, re.IGNORECASE):
            from scene import HelpContextScene
            help_replicas = []
            # Получаем помощь из текущей сцены
            if hasattr(scene, 'get_scene_help'):
                help_replicas = [scene.get_scene_help()]
            elif hasattr(scene, 'scene_help'):
                help_text = getattr(scene, 'scene_help', None)
                help_replicas = [{"text": help_text['text'], "buttons": help_text['buttons']}]
            elif self.global_help_text:
                help_replicas = self.global_help_text()

            return HelpContextScene(help_replicas, scene)
        return super().handle(user_input, scene)


class WaitForNextHandler(Handler):
    def __init__(self, successor=None):
        super().__init__(successor)
        self.waiting_for_next = False

    def handle(self, user_input, scene):
        if scene.is_done():
            help_text = getattr(scene, 'scene_help', None)

            replica = {
                "text": help_text["text"],
                "buttons": help_text["buttons"]
            }
            from scene import HelpContextScene

            return HelpContextScene([replica], scene)

            # Если ожидаем слово "дальше"
        if scene.waiting_for_next:
            if re.search(r"(дальше|далее|продолжи|хорошо|вперёд|ещё)", user_input.lower()):
                scene.waiting_for_next = False
                return scene
            else:
                from scene import HelpContextScene
                replica = {
                    "text": "Скажите \"дальше\", чтобы продолжить.",
                    "buttons": [{"title": "Дальше", "hide": True}]
                }
                return HelpContextScene([replica], scene)

        return super().handle(user_input, scene)


class NextSceneHandler(Handler):
    def __init__(self, load_scene_func, successor=None):
        super().__init__(successor)
        self.load_scene_func = load_scene_func

    def handle(self, user_input, scene):
        if scene.next_scenes:
            for pattern, next_scene_name in scene.next_scenes.items():
                if re.search(pattern, user_input, re.IGNORECASE):
                    return self.load_scene_func(next_scene_name)
        return super().handle(user_input, scene)


class FactHandler(Handler):
    def __init__(self, load_scene_func, successor=None):
        super().__init__(successor)
        self.load_scene_func = load_scene_func

    def handle(self, user_input, scene):
        from scene import FactScene
        if re.search(r"(факт|скучно)", user_input.lower()):
            book_name = getattr(scene, 'book_name', None)
            if book_name is None:
                return super().handle(user_input, scene)
            facts = load_scene_from_file('facts')[book_name]
            buttons = load_scene_from_file('facts')['buttons']

            if facts:
                selected_fact = random.choice(facts)
                selected_fact['buttons'] = buttons
                return FactScene(selected_fact, return_scene=scene)

        return super().handle(user_input, scene)
