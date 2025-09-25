import os
from PyQt6.QtWidgets import QWidget, QComboBox, QLabel, QHBoxLayout
from PyQt6.QtGui import QPixmap

class IconSelector(QWidget):
    """
    Виджет для выбора и предпросмотра иконки из указанной папки
    """
    def __init__(self, icon_dir, label_text="", parent=None):
        super().__init__(parent)
        self.icon_dir = icon_dir
        self.combo = QComboBox()
        self.label = QLabel()
        self.label.setFixedSize(32, 32)
        self.label.setScaledContents(True)
        self.combo.currentIndexChanged.connect(self.update_preview)

        layout = QHBoxLayout(self)
        if label_text:
            layout.addWidget(QLabel(label_text))
        layout.addWidget(self.combo)
        layout.addWidget(self.label)

        self.icons = self._find_icons()
        self.combo.addItems([os.path.basename(path) for path in self.icons])
        self.update_preview(0)

    def _find_icons(self):
        icons = []
        if os.path.isdir(self.icon_dir):
            for fname in os.listdir(self.icon_dir):
                if fname.lower().endswith(('.png', '.jpg', '.bmp', '.ico')):
                    icons.append(os.path.join(self.icon_dir, fname))
            icons.sort()
        return icons

    def update_preview(self, idx):
        if not self.icons:
            self.label.clear()
            return
        pix = QPixmap(self.icons[self.combo.currentIndex()])
        self.label.setPixmap(pix)

    def get_selected_icon_path(self):
        if self.icons:
            return self.icons[self.combo.currentIndex()]
        return None