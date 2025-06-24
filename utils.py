import json
from config import SCENES_DIR


def load_scene_from_file(scene_name):
    with open(f"{SCENES_DIR}/{scene_name}.json", "r", encoding="utf-8") as f:
        return json.load(f)


def format_buttons(buttons):
    result = []
    for btn in buttons:
        if isinstance(btn, str):
            result.append({'title': btn})
        elif isinstance(btn, dict):
            if 'title' not in btn:
                continue
            formatted_button = {k: v for k, v in btn.items() if v is not None}
            result.append(formatted_button)
        else:
            continue
    return result
