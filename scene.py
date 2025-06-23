# scene.py
import re


class Scene:
    def __init__(self, resource: dict, handlers):
        self.handlers = handlers
        self.replics = resource.get("replics", [])
        self.scene_buttons = resource.get("buttons", [])
        self.scene_help = resource.get("help")
        self.next_scenes = resource.get("next_scenes", {})
        self.waiting_for_next = False
        self.book_name = resource.get("book_name")
        self.current_line = 0

    def get_next_replica(self):
        if self.current_line < len(self.replics):
            replica = self.replics[self.current_line]
            self.current_line += 1

            # После вывода реплики ждём "дальше"
            self.waiting_for_next = True
            return replica
        return None

    def get_scene_buttons(self):
        return self.scene_buttons

    def get_scene_help(self):
        return self.scene_help

    def is_done(self):
        return self.current_line >= len(self.replics)

    def handle_input(self, user_input):
        print(f"[Scene.handle_input] Получена фраза: '{user_input}'")
        for i, handler in enumerate(self.handlers):
            print(f"[Scene.handle_input] Вызываю обработчик")
            result = handler.handle(user_input, self)
            if result is not None:
                print(f"[Scene.handle_input] Обработчик {handler.__class__.__name__} вернул результат.")
                return result
        print("[Scene.handle_input] Никакой обработчик не обработал запрос.")
        return self

    def get_next_scenes(self):
        return self.next_scenes


class HelpContextScene:
    def __init__(self, replicas, previous_scene):
        self.replics = replicas
        self.previous_scene = previous_scene
        self.current_line = 0

    def get_next_replica(self):
        if self.current_line < len(self.replics):
            replica = self.replics[self.current_line]
            self.current_line += 1
            return replica
        return None

    def is_done(self):
        return self.current_line >= len(self.replics)

    def get_return_scene(self):
        return self.previous_scene

    def get_scene_buttons(self):
        if hasattr(self.previous_scene, 'get_scene_buttons'):
            return self.previous_scene.get_scene_buttons()
        return []

    def handle_input(self, user_input):
        return self.previous_scene.handle_input(user_input)


class FactScene:
    def __init__(self, facts, return_scene):
        self.facts = facts
        self.return_scene = return_scene
        self.current_line = 0

    def get_next_replica(self):
        if self.current_line == 0:
            fact = self.facts
            self.current_line += 1
            return fact
        return None

    def is_done(self):
        return self.current_line >= 1

    def handle_input(self, user_input):
        return self.return_scene.handle_input(user_input)

    def get_scene_buttons(self):
        if hasattr(self.return_scene, 'get_scene_buttons'):
            return self.return_scene.get_scene_buttons()
        return []

    def get_next_scenes(self):
        return self.return_scene.get_next_scenes()
