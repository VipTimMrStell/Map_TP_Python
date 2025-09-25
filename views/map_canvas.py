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

        self._offset = QPointF(0, 0)
        self._dragging = False
        self._last_mouse_pos = QPoint()

        # --- Храним все маршруты как список списков ---
        self.routes = []                # Все нарисованные маршруты (список списков точек)
        self.current_route = []         # Активный маршрут (точки)
        self.is_route_mode = False
        self.route_color = QColor(Qt.GlobalColor.red)

        # --- Для значков ---
        self.icon_add_mode = False
        self.icon_path_to_add = None
        self.icons_on_map = []  # [(x, y, path), ...]

    def set_route_mode(self, enabled: bool):
        if not enabled and self.current_route:
            # Завершаем текущий маршрут, если был начат
            self.routes.append((self.current_route.copy(), self.route_color))
            self.current_route.clear()
            self.update()
        self.is_route_mode = enabled
        if enabled:
            self.current_route = []

    def set_route_color(self, color: QColor):
        self.route_color = color
        self.update()

    def set_icon_add_mode(self, icon_path):
        self.icon_add_mode = True
        self.icon_path_to_add = icon_path

    def load_background(self, path):
        self.background = QPixmap(path)
        self.zoom = 1.0
        self._offset = QPointF(0, 0)
        self.routes = []
        self.current_route = []
        self.icons_on_map = []
        self.icon_add_mode = False
        self.icon_path_to_add = None
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.background:
            w = self.background.width() * self.zoom
            h = self.background.height() * self.zoom
            painter.translate(self._offset)
            painter.drawPixmap(0, 0, int(w), int(h), self.background)

            # --- Рисуем значки ---
            for x, y, icon_path in self.icons_on_map:
                pix = QPixmap(icon_path)
                pix = pix.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                draw_x = x * self.zoom - 16
                draw_y = y * self.zoom - 16
                painter.drawPixmap(int(draw_x), int(draw_y), pix)
        else:
            painter.translate(self._offset)

        # --- Рисуем все завершённые маршруты ---
        for route, color in self.routes:
            if len(route) > 1:
                pen = QPen(color, 3)
                painter.setPen(pen)
                points = [
                    QPointF(x * self.zoom, y * self.zoom)
                    for (x, y) in route
                ]
                for i in range(len(points) - 1):
                    painter.drawLine(points[i], points[i + 1])

        # --- Рисуем текущий маршрут, если он есть ---
        if len(self.current_route) > 1:
            pen = QPen(self.route_color, 3)
            painter.setPen(pen)
            points = [
                QPointF(x * self.zoom, y * self.zoom)
                for (x, y) in self.current_route
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
        if self.icon_add_mode and event.button() == Qt.MouseButton.LeftButton and self.background:
            x = (event.position().x() - self._offset.x()) / self.zoom
            y = (event.position().y() - self._offset.y()) / self.zoom
            self.icons_on_map.append((x, y, self.icon_path_to_add))
            self.icon_add_mode = False
            self.icon_path_to_add = None
            self.update()
            return

        if self.is_route_mode and event.button() == Qt.MouseButton.LeftButton and self.background:
            x = (event.position().x() - self._offset.x()) / self.zoom
            y = (event.position().y() - self._offset.y()) / self.zoom
            self.current_route.append((x, y))
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
        self.routes = []
        self.current_route = []
        self.update()

    def remove_last_route(self):
        if self.routes:
            self.routes.pop()
            self.update()