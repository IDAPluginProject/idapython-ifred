from typing import Callable, Optional
from .qt_bindings import *

from .action import Action
from .filter import SearchService
from .PaletteItems import PaletteItems
from .utils import loadFile

ActionHandler = Callable[[Action], bool]

class PaletteFrame(QFrame):
    item_clicked = Signal(Action)

    def __init__(self, parent: QWidget, name: str, close_key: str, search_service: SearchService):
        super().__init__(parent)
        self.name = name
        self.registered_keys = {}

        # Create widgets
        self.searchbox = QLineEdit(self)
        self.searchbox.setAttribute(Qt.WA_MacShowFocusRect, 0)

        self.items = PaletteItems(self, name, search_service)
        self.items.setAttribute(Qt.WA_MacShowFocusRect, 0)

        # Layout setup
        layout = QVBoxLayout(self)
        layout.addWidget(self.searchbox)
        layout.addWidget(self.items)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Connect signals
        self.searchbox.returnPressed.connect(self._handle_return)
        self.searchbox.textChanged.connect(self._handle_text_changed)
        self.items.clicked.connect(self._handle_item_clicked)
        self.item_clicked.connect(lambda action:
            self.items.model().searchService().itemClicked.emit(action.id))

        # Install event filters
        self.searchbox.installEventFilter(self)
        self.items.installEventFilter(self)

        # Set initial filter
        self.items.model().setFilter("")

        # Register shortcuts
        if close_key:
            self.register_shortcut(QKeySequence(close_key), lambda: self.window().close())

        self.register_shortcut(QKeySequence("Ctrl+J"), lambda: self._arrow_pressed(-1))
        self.register_shortcut(QKeySequence("Ctrl+K"), lambda: self._arrow_pressed(1))
        self.register_shortcut(QKeySequence("Esc"), lambda: self.window().close())

    def register_shortcut(self, sequence: QKeySequence, callback: Callable):
        # Handle Meta key like Ctrl on macOS
        key_str = sequence.toString().replace("Meta+", "Ctrl+")
        sequence = QKeySequence(key_str)

        shortcut = QShortcut(sequence, self)
        shortcut.activated.connect(callback)
        self.registered_keys[sequence] = shortcut
        return shortcut

    def _arrow_pressed(self, delta: int):
        new_row = self.items.currentIndex().row() + delta
        row_count = self.items.model().rowCount()

        new_row = max(0, min(new_row, row_count - 1))
        self.items.setCurrentIndex(self.items.model().index(new_row, 0))

    def eventFilter(self, obj: QWidget, event: QEvent) -> bool:
        if event.type() == QEvent.KeyPress:
            key_event: QKeyEvent = event
            if QT_API == 'PySide6':
                sequence = QKeySequence(key_event.keyCombination())
            else:
                # TODO
                sequence = QKeySequence(key_event.key(), int(key_event.modifiers()))

            if sequence in self.registered_keys:
                self.registered_keys[sequence].activated.emit()
                return True

            if key_event.key() in (Qt.Key_Down, Qt.Key_Up):
                self._arrow_pressed(1 if key_event.key() == Qt.Key_Down else -1)
                return True

            if key_event.key() in (Qt.Key_PageDown, Qt.Key_PageUp):
                event.ignore()
                self.items.keyPressEvent(key_event)
                return True

        elif event.type() == QEvent.FocusOut:
            focus_event = event
            if (obj == self.searchbox and
                focus_event.reason() == Qt.MouseFocusReason):
                self.searchbox.setFocus()
                return True

        elif event.type() == QEvent.ShortcutOverride:
            event.accept()
            return True

        return super().eventFilter(obj, event)

    def showEvent(self, event):
        self.searchbox.setFocus()

    def setPlaceholderText(self, placeholder: str):
        self.searchbox.setPlaceholderText(placeholder)

    def _handle_return(self):
        if self.items.model().rowCount():
            action = self.items.currentIndex().data()
            self.window().hide()
            self.item_clicked.emit(action)
            self.window().close()

    def _handle_text_changed(self, text: str):
        self.style().polish(self.searchbox)
        self.items.model().setFilter(text)

    def _handle_item_clicked(self, index):
        action = index.data()
        self.window().hide()
        self.item_clicked.emit(action)
        self.window().close()
