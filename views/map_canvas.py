from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPixmap, QPainter, QMouseEvent, QWheelEvent
from PyQt6.QtCore import Qt, QPoint, QPointF
from models.map_model import MapModel

class MapCanvas(QWidget):
    def __init__(self, model: MapModel, parent=None):
        super().__init__(parent)
        self.model = model
        self.background = None

        self.zoom = 1.0
        self._min_zoom = 0.2
        self._max_zoom = 5.0

        self._dragging = False
        self._last_mouse_pos = QPoint()
        self._offset = QPointF(0, 0)  # смещение карты при панорамировании

    def load_background(self, path):
        self.background = QPixmap(path)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.background:
            w = self.background.width() * self.zoom
            h = self.background.height() * self.zoom
            painter.translate(self._offset)
            painter.drawPixmap(0, 0, int(w), int(h), self.background)

    def zoom_in(self):
        self.zoom = min(self.zoom * 1.2, self._max_zoom)
        self.update()

    def zoom_out(self):
        self.zoom = max(self.zoom * 0.83, self._min_zoom)
        self.update()

    def reset_view(self):
        self.zoom = 1.0
        self._offset = QPointF(0, 0)
        self.update()