from .qt_bindings import *
from typing import List, Optional
from dataclasses import dataclass

from .action import Action

class PaletteFilter(QAbstractItemModel):
    startSearching = Signal(str)
    item_clicked = Signal(Action)
    filteringDone = Signal(int)  # Signal for when filtering is complete

    def __init__(self, parent: QWidget, palette_name: str, search_service: 'SearchService'):
        super().__init__(parent)
        self.shown_items: List[Action] = []
        self.keyword: str = ""
        self.worker_thread = QThread(self)
        self.search_service = search_service
        self.timer = QTimer()
        self.timer.setSingleShot(True)


        if self.search_service.runInSeparateThread():
            self.worker_thread.destroyed.connect(self.search_service.deleteLater)
            self.search_service.setParent(None)
            self.search_service.moveToThread(self.worker_thread)
            # XXX PyQt5 differ from PySide6 and native Qt

            self.worker_thread.start()
        else:
            self.search_service.setParent(self)

        # Connect signals and slots with `search_service`
        self.startSearching.connect(self.search_service.doSearch)
        self.item_clicked.connect(self.search_service.handle_item_clicked)
        self.search_service.doneSearching.connect(self.onDoneSearching)

        # NOTE self is a QObject now, so can't find instance method
        def onDestroy():
            self.search_service.cancel()
            self.worker_thread.quit()
            self.worker_thread.wait()
        # self.destroyed.connect(self.onDestroy)
        self.destroyed.connect(onDestroy)

    def setFilter(self, keyword: str) -> None:
        if self.timer.isActive():
            self.timer.stop()
        
        # Safely disconnect previous connections to avoid accumulation
        try:
            self.timer.timeout.disconnect()
        except TypeError:
            # No connections exist yet, which is fine
            pass
        
        # Capture keyword in closure (not lambda parameter)
        self.timer.timeout.connect(lambda: (
            self.search_service.cancel(),
            self.startSearching.emit(keyword)
        ))
        self.timer.start(300)  # 300ms delay for debouncing

    def filter(self) -> str:
        return self.keyword

    def searchService(self) -> 'SearchService':
        return self.search_service

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        return self.createIndex(row, column)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self.shown_items[index.row()]
        elif role == Qt.UserRole:
            return self.keyword
        return None

    def parent(self, index: QModelIndex) -> QModelIndex:
        return QModelIndex()

    def columnCount(self, parent: QModelIndex) -> int:
        return 1

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.shown_items)

    def handle_item_clicked(self, action):
        self.item_clicked.emit(action)

    def onDoneSearching(self, keyword: str, items: List[Action], recent_count: int) -> None:
        self.layoutAboutToBeChanged.emit()
        self.shown_items = items
        self.keyword = keyword
        self.layoutChanged.emit()
        self.filteringDone.emit(recent_count)


class SearchService(QObject):
    startSearching = Signal(str)  # Signal for search request
    itemClicked = Signal(str)     # Signal for item selection
    doneSearching = Signal(str, list, int)  # Signal for search completion

    def __init__(self, parent: QObject):
        super().__init__(parent)

    def search(self, keyword: str) -> None:
        self.cancel()
        self.startSearching.emit(keyword)

    def cancel(self) -> None:
        raise NotImplementedError("Subclasses must implement cancel()")

    def runInSeparateThread(self) -> bool:
        raise NotImplementedError("Subclasses must implement runInSeparateThread()")

    def connectSignals(self):
        raise NotImplementedError("Subclasses must implement connectSignals()")
