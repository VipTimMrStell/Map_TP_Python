from typing import List, Dict, Any

class MapModel:
    def __init__(self):
        self.background_path: str = ""
        self.elements: List[Dict[str, Any]] = []

    def load_background(self, path: str):
        self.background_path = path

    def add_element(self, element: Dict[str, Any]):
        self.elements.append(element)

    def clear(self):
        self.background_path = ""
        self.elements.clear()