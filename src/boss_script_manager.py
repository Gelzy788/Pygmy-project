import json
import random
from pathlib import Path


class BossScriptManager:
    def __init__(self):
        self.scripts = self._load_scripts()
        self.current_script = None

    def _load_scripts(self):
        script_path = Path(__file__).parent / "data" / "boss_scripts.json"
        with open(script_path, 'r') as f:
            return json.load(f)

    def load_script(self, script_name):
        if script_name in self.scripts:
            self.current_script = self.scripts[script_name]
            return True
        return False

    def get_shield_sequence(self):
        if self.current_script:
            return self.current_script.get("shield_sequence", [])
        return []

    def get_attack_sequence(self):
        if self.current_script:
            return self.current_script.get("attack_sequence", [])
        return []

    def get_random_attack_config(self):
        if self.current_script:
            return self.current_script.get("random_attacks", None)
        return None
