# Try PyQt5 (ida pro)
try:
    from PyQt5 import QtCore, QtGui, QtWidgets, uic
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QFrame, QLineEdit,
        QVBoxLayout, QShortcut, QStyle, QStyledItemDelegate,
        QStyleOptionViewItem, QListView, QAbstractItemView,
        QGraphicsDropShadowEffect)
    from PyQt5.QtCore import (
        Qt, QRegularExpression, QThread, QObject,
        QAbstractEventDispatcher, QTimer, QFileSystemWatcher,
        QDir, QFile, QIODevice, QEvent, QSize, QRectF,
        QAbstractItemModel, QModelIndex, QSettings)
    from PyQt5.QtGui import (
        QFocusEvent, QKeyEvent, QKeySequence, QColor,
        QGuiApplication, QScreen, QPainter, QTextDocument,
        QTextOption)

    Signal = QtCore.pyqtSignal
    Slot = QtCore.pyqtSlot
    QT_API = 'PyQt5'
except ImportError:
    # Then try PySide6 (for test)
    try:
        from PySide6 import QtCore, QtGui, QtWidgets, QtUiTools
        from PySide6.QtWidgets import (
            QApplication, QMainWindow, QWidget, QFrame, QLineEdit,
            QVBoxLayout, QStyle, QStyledItemDelegate,
            QStyleOptionViewItem, QListView, QAbstractItemView,
            QGraphicsDropShadowEffect)
        from PySide6.QtCore import (
            Qt, QRegularExpression, QThread, QObject, Signal,
            QAbstractEventDispatcher, QTimer, QFileSystemWatcher,
            QDir, QFile, QIODevice, QEvent, QSize, QRectF,
            QAbstractItemModel, QModelIndex, QSettings)
        from PySide6.QtGui import (
            QFocusEvent, QKeyEvent, QKeySequence, QColor, QShortcut,
            QGuiApplication, QScreen, QPainter, QTextDocument,
            QTextOption)
        QT_API = 'PySide6'
    except ImportError as e:
        print(e)
        # Then try PySide2
        try:
            from PySide2 import QtCore, QtGui, QtWidgets, QtUiTools
            QT_API = 'PySide2'
        except ImportError:
            # Finally, try PyQt6
            try:
                from PyQt6 import QtCore, QtGui, QtWidgets, uic
                QT_API = 'PyQt6'
            except ImportError:
                raise ImportError("No Qt binding found. Please install PySide6, PyQt6, PySide2, or PyQt5.")

# Common aliases for consistency
if QT_API.startswith('PyQt'):
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot

# Function to load UI files (handles differences between uic.loadUi and QtUiTools.QUiLoader)
def load_ui(uifile):
    if QT_API in ['PySide6', 'PySide2']:
        loader = QtUiTools.QUiLoader()
        uif = QtCore.QFile(uifile)
        uif.open(QtCore.QFile.ReadOnly)
        result = loader.load(uif)
        uif.close()
        return result
    elif QT_API in ['PyQt6', 'PyQt5']:
        return uic.loadUi(uifile)

# __all__ = ['QtCore', 'QtGui', 'QtWidgets', 'load_ui', 'QT_API']