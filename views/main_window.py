from PyQt6.QtWidgets import QMainWindow, QFileDialog, QToolBar, QMessageBox
from PyQt6.QtGui import QIcon
from views.map_canvas import MapCanvas
from models.map_model import MapModel
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QToolBar, QMessageBox
from PyQt6.QtGui import QIcon, QAction

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Topographic Map Editor")
        self.resize(1200, 800)

        self.model = MapModel()
        self.canvas = MapCanvas(self.model)
        self.setCentralWidget(self.canvas)

        self._create_toolbar()
        self._create_menus()

    def _create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        open_action = QAction("Выбрать карту", self)
        open_action.triggered.connect(self.open_map)
        toolbar.addAction(open_action)

        zoom_in_action = QAction("Масштаб +", self)
        zoom_in_action.triggered.connect(self.canvas.zoom_in)
        toolbar.addAction(zoom_in_action)

        zoom_out_action = QAction("Масштаб -", self)
        zoom_out_action.triggered.connect(self.canvas.zoom_out)
        toolbar.addAction(zoom_out_action)

        # --- КНОПКА РИСОВАНИЯ МАРШРУТА ---
        self.route_action = QAction("Режим: Маршрут", self)
        self.route_action.setCheckable(True)
        self.route_action.toggled.connect(self.toggle_route_mode)
        toolbar.addAction(self.route_action)

        clear_route_action = QAction("Очистить маршрут", self)
        clear_route_action.triggered.connect(self.canvas.clear_route)
        toolbar.addAction(clear_route_action)

    def toggle_route_mode(self, checked):
        self.canvas.set_route_mode(checked)

    def _create_menus(self):
        pass

    def open_map(self):
        path, _ = QFileDialog.getOpenFileName(self, "Открыть изображение карты", "", "Images (*.png *.jpg *.bmp)")
        if path:
            self.model.load_background(path)
            self.canvas.load_background(path)
        else:
            QMessageBox.warning(self, "Файл не выбран", "Выберите файл изображения.")