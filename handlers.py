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
        print(f"[ExitHandler] Проверяю фразу: '{user_input}'")
        if re.search(r"(хватит|стоп|выход|пока|завершить)", user_input):
            print("[ExitHandler] Найдено ключевое слово для выхода")
            return 'Exit'
        return super().handle(user_input, scene)


# handlers.py
class HelpHandler(Handler):
    def __init__(self, global_help_text, successor=None):
        super().__init__(successor)
        self.global_help_text = global_help_text

    def handle(self, user_input, scene):
        print('это хелп')
        if re.search(r"(помощь|помог|что делать)", user_input, re.IGNORECASE):
            from scene import HelpContextScene

            help_text = getattr(scene, 'scene_help', None)
            help_replicas = []

            if help_text:
                help_replicas = [{"text": help_text['text'], "buttons": help_text['buttons']}]  # add buttons
            elif self.global_help_text:
                help_replicas = self.global_help_text

            return HelpContextScene(help_replicas, scene)

        return super().handle(user_input, scene)


class WaitForNextHandler(Handler):
    def __init__(self, successor=None):
        super().__init__(successor)
        self.waiting_for_next = False

    def handle(self, user_input, scene):
        print('дальше внутри сцены')
        if scene.is_done():
            print("[WaitForNextHandler] Сцена завершена. Предлагаем помощь")
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
                print("[WaitForNextHandler] Продолжаем сцену")
                scene.waiting_for_next = False
                return scene
            else:
                from scene import HelpContextScene
                print("[WaitForNextHandler] Ждём 'дальше'")
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
        # print('это некст')
        # if not getattr(scene, 'book_name', None):
        #     user_input = user_input.lower()
        #     if re.search(r'(преступлени|наказани)', user_input):
        #         return self.load_scene_func("crime_and_punishment")
        #     elif re.search(r'(идиот)', user_input):
        #         return self.load_scene_func("idiot")

        if scene.next_scenes:
            print(scene.next_scenes)
            for pattern, next_scene_name in scene.next_scenes.items():
                if re.search(pattern, user_input, re.IGNORECASE):
                    return self.load_scene_func(next_scene_name)
        return super().handle(user_input, scene)


class FactHandler(Handler):
    def __init__(self, load_scene_func, successor=None):
        super().__init__(successor)
        self.load_scene_func = load_scene_func

    def handle(self, user_input, scene):
        print(f"[FactHandler] Получена фраза: '{user_input}'")
        from scene import FactScene
        if re.search(r"(факт|скучно)", user_input.lower()):
            print("[FactHandler] Запрос на показ факта")

            book_name = getattr(scene, 'book_name', None)
            print(book_name)
            if book_name is None:
                return super().handle(user_input, scene)
            facts = load_scene_from_file('facts')[book_name]
            buttons = load_scene_from_file('facts')['buttons']

            if facts:
                selected_fact = random.choice(facts)
                selected_fact['buttons'] = buttons
                return FactScene(selected_fact, return_scene=scene)

        return super().handle(user_input, scene)

        #     # Берём название произведения из текущей сцены
        #     book_name = getattr(scene, 'book_name', None)
        #     print(book_name)
        #     if isinstance(book_name, type(None)):
        #         return super().handle(user_input, scene)
        #     # Загружаем факты
        #     load_facts = load_scene_from_file('facts')
        #     print(load_facts)
        #     facts = load_facts[book_name]
        #     buttons = load_scene_from_file('facts')['buttons']
        #
        #     # Создаём временную сцену с фактами
        #     if facts:
        #         selected_fact = random.choice(facts)
        #         selected_fact['buttons'] = buttons
        #         return FactScene(selected_fact, load_facts, return_scene=scene)
        #
        # return super().handle(user_input, scene)
