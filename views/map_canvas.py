from PyQt6.QtWidgets import QWidget, QColorDialog
from PyQt6.QtGui import QPainter, QPixmap, QMouseEvent, QWheelEvent, QPen, QColor
from PyQt6.QtCore import Qt, QPoint, QPointF

class MapCanvas(QWidget):
    def __init__(self, model=None, parent=None):
        super().__init__(parent)
        self.model = model
        self.background = None

        self.zoom = 1.0
        self._min_zoom = 0.2
        self._max_zoom = 5.0

        self._offset = QPointF(0, 0)  # Смещение карты (панорамирование)
        self._dragging = False
        self._last_mouse_pos = QPoint()

        # === Для маршрута ===
        self.route_points = []  # точки маршрута в координатах карты (float)
        self.is_route_mode = False
        self.route_color = QColor(Qt.GlobalColor.red)  # Цвет маршрута по умолчанию

    def set_route_mode(self, enabled: bool):
        self.is_route_mode = enabled

    def set_route_color(self, color: QColor):
        self.route_color = color
        self.update()

    def load_background(self, path):
        self.background = QPixmap(path)
        self.zoom = 1.0
        self._offset = QPointF(0, 0)
        self.route_points = []
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.background:
            w = self.background.width() * self.zoom
            h = self.background.height() * self.zoom
            painter.translate(self._offset)
            painter.drawPixmap(0, 0, int(w), int(h), self.background)
        # --- Рисуем маршрут ---
        if len(self.route_points) > 1:
            pen = QPen(self.route_color, 3)
            painter.setPen(pen)
            points = [
                QPointF(x * self.zoom, y * self.zoom)
                for (x, y) in self.route_points
            ]
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i + 1])

    def wheelEvent(self, event: QWheelEvent):
        if not self.background:
            return
        angle = event.angleDelta().y()
        factor = 1.15 if angle > 0 else 0.85
        old_zoom = self.zoom
        new_zoom = old_zoom * factor
        new_zoom = max(self._min_zoom, min(self._max_zoom, new_zoom))
        if abs(new_zoom - old_zoom) < 1e-6:
            return
        mouse_pos = event.position()
        rel_x = (mouse_pos.x() - self._offset.x()) / old_zoom
        rel_y = (mouse_pos.y() - self._offset.y()) / old_zoom
        self.zoom = new_zoom
        self._offset = QPointF(
            mouse_pos.x() - rel_x * self.zoom,
            mouse_pos.y() - rel_y * self.zoom
        )
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if self.is_route_mode and event.button() == Qt.MouseButton.LeftButton and self.background:
            # Координаты клика — в координаты карты!
            x = (event.position().x() - self._offset.x()) / self.zoom
            y = (event.position().y() - self._offset.y()) / self.zoom
            self.route_points.append((x, y))
            self.update()
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._dragging:
            delta = event.pos() - self._last_mouse_pos
            self._offset += QPointF(delta.x(), delta.y())
            self._last_mouse_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False

    def zoom_in(self):
        center = QPointF(self.width() / 2, self.height() / 2)
        self._apply_zoom(1.2, center)

    def zoom_out(self):
        center = QPointF(self.width() / 2, self.height() / 2)
        self._apply_zoom(0.83, center)

    def _apply_zoom(self, factor, center):
        if not self.background:
            return
        old_zoom = self.zoom
        new_zoom = old_zoom * factor
        new_zoom = max(self._min_zoom, min(self._max_zoom, new_zoom))
        if abs(new_zoom - old_zoom) < 1e-6:
            return
        rel_x = (center.x() - self._offset.x()) / old_zoom
        rel_y = (center.y() - self._offset.y()) / old_zoom
        self.zoom = new_zoom
        self._offset = QPointF(
            center.x() - rel_x * self.zoom,
            center.y() - rel_y * self.zoom
        )
        self.update()

    def clear_route(self):
        self.route_points = []
        self.update()