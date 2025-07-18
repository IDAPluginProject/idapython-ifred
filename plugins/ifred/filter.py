from .qt_bindings import *
from typing import List, Optional
from dataclasses import dataclass

from .action import Action

class PaletteFilter(QAbstractItemModel):
    filteringDone = Signal(int)  # Signal for when filtering is complete

    def __init__(self, parent: QWidget, palette_name: str, search_service: 'SearchService'):
        super().__init__(parent)
        self.shown_items: List[Action] = []
        self.keyword: str = ""
        self.search_service = None
        self.search_worker = QThread(self)

        self.setSearchService(search_service)
        self.search_service.doneSearching.connect(self.onDoneSearching, Qt.QueuedConnection)

        # NOTE self is a QObject now, so can't find instance method
        def onDestroy():
            self.search_service.cancel()
            self.search_worker.quit()
            self.search_worker.wait()
        # self.destroyed.connect(self.onDestroy)
        self.destroyed.connect(onDestroy)

    def setFilter(self, keyword: str) -> None:
        self.search_service.search(keyword)

    def filter(self) -> str:
        return self.keyword

    def searchService(self) -> 'SearchService':
        return self.search_service

    def setSearchService(self, new_service: 'SearchService') -> None:
        self.search_service = new_service

        if self.search_service.runInSeparateThread():
            self.search_worker.destroyed.connect(self.search_service.deleteLater)
            self.search_service.setParent(None)
            self.search_service.moveToThread(self.search_worker)
            # XXX PyQt5 differ from PySide6 and native Qt
            self.search_service.connectSignals()
            self.search_worker.start()
        else:
            self.search_service.setParent(self)
            self.search_service.connectSignals()

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

    def onDoneSearching(self, keyword: str, items: List[Action], recent_count: int) -> None:
        self.layoutAboutToBeChanged.emit()
        self.shown_items = items
        self.keyword = keyword
        self.layoutChanged.emit()
        self.filteringDone.emit(recent_count)

    def onDestroy(self) -> None:
        self.search_service.cancel()
        self.search_worker.quit()
        self.search_worker.wait()


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
