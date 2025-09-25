from PyQt6.QtWidgets import QMainWindow, QFileDialog, QToolBar, QAction, QMessageBox
from PyQt6.QtGui import QIcon
from views.map_canvas import MapCanvas
from models.map_model import MapModel

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

        open_action = QAction(QIcon(), "Выбрать карту", self)
        open_action.triggered.connect(self.open_map)
        toolbar.addAction(open_action)

        # TODO: add other tool actions here

    def _create_menus(self):
        # Optionally add menus here
        pass

    def open_map(self):
        path, _ = QFileDialog.getOpenFileName(self, "Открыть изображение карты", "", "Images (*.png *.jpg *.bmp)")
        if path:
            self.model.load_background(path)
            self.canvas.load_background(path)
        else:
            QMessageBox.warning(self, "Файл не выбран", "Выберите файл изображения.")
