from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtCore import Qt
from models.map_model import MapModel

class MapCanvas(QWidget):
    def __init__(self, model: MapModel, parent=None):
        super().__init__(parent)
        self.model = model
        self.background = None

    def load_background(self, path):
        self.background = QPixmap(path)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.background:
            # Масштабируем изображение до размера виджета пока что
            painter.drawPixmap(self.rect(), self.background)
        # TODO: draw elements (routes, icons, text)