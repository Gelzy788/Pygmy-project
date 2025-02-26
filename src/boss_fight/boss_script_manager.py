import json
import os


class BossScriptManager:
    def __init__(self):
        self.current_time = 0
        self.script = None

    def load_script(self, script_path):
        try:
            # Получаем абсолютный путь к файлу скрипта
            abs_path = os.path.join(os.path.dirname(
                os.path.dirname(os.path.dirname(__file__))), script_path)

            with open(abs_path, 'r') as f:
                self.script = json.load(f)
                return True
        except FileNotFoundError:
            print(f"Error: Script '{script_path}' not found!")
            return False
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in script file '{script_path}'")
            return False

    def get_shield_sequence(self):
        if self.script:
            return self.script.get("shield_sequence", [])
        return []

    def get_attack_sequence(self):
        if self.script:
            return self.script.get("attack_sequence", [])
        return []

    def get_random_attack_config(self):
        if self.script:
            return self.script.get("random_attacks", None)
        return None
