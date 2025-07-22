import json
from typing import Callable, Optional
from .qt_bindings import *

from .utils import loadFile, load_json
from .PaletteFrame import PaletteFrame, ActionHandler
from .basic_service import BasicService

class CommandPalette(QMainWindow):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)  # Enable window transparency

        # Set style sheet from window.css
        self.setStyleSheet(loadFile("theme/window.css"))

        # Set shadow effect from styles.json
        shadow = QGraphicsDropShadowEffect(self)

        styles = load_json("theme/styles.json")
        shadow_width = styles.get("shadow-width", 0)

        shadow.setBlurRadius(shadow_width)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0)

        self.setGraphicsEffect(shadow)
        self.setContentsMargins(shadow_width, shadow_width, shadow_width, shadow_width)

    def show(self, name: str, placeholder: str, actions_or_service, close_key: str, func: ActionHandler):
        if isinstance(actions_or_service, list):
            search_service = BasicService(None, name, actions_or_service)
        else:
            search_service = actions_or_service

        inner = PaletteFrame(self, name, close_key, search_service)
        self.setCentralWidget(inner)
        inner.setItemClickedHandler(func)
        inner.setPlaceholderText(placeholder)

        super().show()
        self._center_widgets(self, self.parentWidget())
        self.activateWindow()

    def focusOutEvent(self, event: QFocusEvent):
        self.close()

    @staticmethod
    def _center_widgets(window: QWidget, host: Optional[QWidget] = None):
        if host:
            host_rect = host.geometry()
            window.move(host_rect.center() - window.rect().center())
        else:
            screen_geometry = QGuiApplication.screens()[0].geometry()
            x = (screen_geometry.width() - window.width()) // 2
            y = (screen_geometry.height() - window.height()) // 2
            window.move(x, y)

