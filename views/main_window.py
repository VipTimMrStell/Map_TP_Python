from PyQt6.QtWidgets import QMainWindow, QFileDialog, QToolBar, QMessageBox, QColorDialog, QDialog, QVBoxLayout, QPushButton
from PyQt6.QtGui import QIcon, QAction
from views.map_canvas import MapCanvas
from views.icon_tool import IconSelector
from models.map_model import MapModel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Topographic Map Editor")
        self.resize(1200, 800)

        self.model = MapModel()
        self.canvas = MapCanvas(self.model)
        self.setCentralWidget(self.canvas)
        self.selected_icon_path = None

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

        # --- КНОПКА УДАЛЕНИЯ ПОСЛЕДНЕГО МАРШРУТА ---
        remove_last_action = QAction("Удалить последний маршрут", self)
        remove_last_action.triggered.connect(self.canvas.remove_last_route)
        toolbar.addAction(remove_last_action)

        # --- КНОПКА ОЧИСТКИ ВСЕХ МАРШРУТОВ ---
        clear_route_action = QAction("Очистить все маршруты", self)
        clear_route_action.triggered.connect(self.canvas.clear_route)
        toolbar.addAction(clear_route_action)

        # --- КНОПКА ВЫБОРА ЦВЕТА ---
        color_action = QAction("Цвет маршрута", self)
        color_action.triggered.connect(self.choose_route_color)
        toolbar.addAction(color_action)

        # --- КНОПКИ ДОБАВЛЕНИЯ ИКОНКИ ---
        add_blue_icon_action = QAction("Добавить синий значок", self)
        add_blue_icon_action.triggered.connect(self.select_blue_icon)
        toolbar.addAction(add_blue_icon_action)

        add_red_icon_action = QAction("Добавить красный значок", self)
        add_red_icon_action.triggered.connect(self.select_red_icon)
        toolbar.addAction(add_red_icon_action)

    def select_blue_icon(self):
        self.open_icon_selector("materials/icons_blue", "Синий значок")

    def select_red_icon(self):
        self.open_icon_selector("materials/icons_red", "Красный значок")

    def open_icon_selector(self, folder_path, label):
        dialog = QDialog(self)
        dialog.setWindowTitle("Выберите значок")
        layout = QVBoxLayout(dialog)
        selector = IconSelector(folder_path, label + ": ")
        layout.addWidget(selector)
        ok_btn = QPushButton("OK")
        layout.addWidget(ok_btn)

        def on_ok():
            self.selected_icon_path = selector.get_selected_icon_path()
            dialog.accept()
        ok_btn.clicked.connect(on_ok)

        if dialog.exec():
            if self.selected_icon_path:
                self.canvas.set_icon_add_mode(self.selected_icon_path)
        else:
            self.selected_icon_path = None

    def choose_route_color(self):
        color = QColorDialog.getColor(self.canvas.route_color, self, "Выберите цвет маршрута")
        if color.isValid():
            self.canvas.set_route_color(color)

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