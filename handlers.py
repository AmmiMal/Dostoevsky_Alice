# handlers.py
import re
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
        print(f"[ExitHandler] Проверяю фразу: '{user_input}'")
        if re.search(r"(хватит|стоп|выход|пока)", user_input):
            print("[ExitHandler] Найдено ключевое слово для выхода")
            return 'Exit'
        return super().handle(user_input, scene)


# handlers.py
class HelpHandler(Handler):
    def __init__(self, global_help_text, successor=None):
        super().__init__(successor)
        self.global_help_text = global_help_text

    def handle(self, user_input, scene):
        if re.search(r"(помощь|помог)", user_input, re.IGNORECASE):
            from scene import HelpContextScene

            help_text = getattr(scene, 'scene_help', None)
            help_replicas = []

            if help_text:
                help_replicas = [{"text": help_text, "buttons": [{"title": "Дальше", "hide": True}]}]  # add buttons
            elif self.global_help_text:
                help_replicas = self.global_help_text

            return HelpContextScene(help_replicas, scene)

        return super().handle(user_input, scene)


class WaitForNextHandler(Handler):
    def __init__(self, successor=None):
        super().__init__(successor)
        self.waiting_for_next = False

    def handle(self, user_input, scene):
        if hasattr(scene, 'waiting_for_next') and scene.waiting_for_next:
            if re.search(r"(дальше|далее|продолжи|вперёд|ещё)", user_input, re.IGNORECASE):
                scene.waiting_for_next = False
                return scene  # продолжаем текущую сцену
            else:
                from scene import HelpContextScene
                # Если пользователь не сказал "дальше"
                replica = {"text": "Скажите \"дальше\", чтобы продолжить.",
                           "buttons": [{"title": "Дальше", "hide": True}]}
                return HelpContextScene([replica], scene)
        return super().handle(user_input, scene)


class NextSceneHandler(Handler):
    def __init__(self, load_scene_func, successor=None):
        super().__init__(successor)
        self.load_scene_func = load_scene_func

    def handle(self, user_input, scene):
        print(scene)
        if scene.next_scenes:
            for pattern, next_scene_name in scene.next_scenes.items():
                if re.search(pattern, user_input, re.IGNORECASE):
                    return self.load_scene_func(next_scene_name)
        return super().handle(user_input, scene)
