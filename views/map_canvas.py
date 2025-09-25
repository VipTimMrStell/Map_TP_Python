from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPixmap, QMouseEvent, QWheelEvent
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

    def load_background(self, path):
        self.background = QPixmap(path)
        self.zoom = 1.0
        self._offset = QPointF(0, 0)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.background:
            w = self.background.width() * self.zoom
            h = self.background.height() * self.zoom
            # Сдвигаем изображение по смещению
            painter.translate(self._offset)
            painter.drawPixmap(0, 0, int(w), int(h), self.background)
        # TODO: здесь можно отрисовывать аннотации

    def wheelEvent(self, event: QWheelEvent):
        if not self.background:
            return
        # Зум относительно положения курсора
        angle = event.angleDelta().y()
        factor = 1.15 if angle > 0 else 0.85
        old_zoom = self.zoom
        new_zoom = old_zoom * factor
        # Ограничения
        new_zoom = max(self._min_zoom, min(self._max_zoom, new_zoom))
        if abs(new_zoom - old_zoom) < 1e-6:
            return

        # Координаты курсора относительно виджета
        mouse_pos = event.position()
        # Переводим их в координаты карты до зума
        rel_x = (mouse_pos.x() - self._offset.x()) / old_zoom
        rel_y = (mouse_pos.y() - self._offset.y()) / old_zoom

        # После зума надо скорректировать offset, чтобы точка под мышкой осталась на месте
        self.zoom = new_zoom
        self._offset = QPointF(
            mouse_pos.x() - rel_x * self.zoom,
            mouse_pos.y() - rel_y * self.zoom
        )
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
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
        # Зум к центру виджета
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

'''
    def reset_view(self):
        if self.background:
            self.zoom = 1.0
            # Центрируем картинку в виджете
            img_w = self.background.width()
            img_h = self.background.height()
            win_w = self.width()
            win_h = self.height()
            offset_x = (win_w - img_w) / 2
            offset_y = (win_h - img_h) / 2
            self._offset = QPointF(offset_x, offset_y)
        else:
            self.zoom = 1.0
            self._offset = QPointF(0, 0)
        self.update()
'''