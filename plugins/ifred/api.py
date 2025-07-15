from typing import Callable, List, Optional
from .qt_bindings import *
from .action import Action
from .CommandPalette import CommandPalette

g_current_widget = None
# Type hint for plugin path handler
PluginPathHandler = Callable[[str], str]
pluginPath: Optional[PluginPathHandler] = None

def post_to_thread(func: Callable, thread: QThread = None) -> None:
    if thread is None:
        thread = QApplication.instance().thread()

    obj = QAbstractEventDispatcher.instance(thread)
    assert obj is not None

    src = QObject()
    # FIXME
    # src.destroyed.connect(obj, func, Qt.ConnectionType.QueuedConnection)
    src.destroyed.connect(func, Qt.ConnectionType.QueuedConnection)

def post_to_timer(func: Callable, timeout: int = 0) -> None:
    print(111)
    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(func)
    timer.start(timeout)

def get_main_window() -> QWidget:
    # This is not too expensive
    for widget in QApplication.instance().topLevelWidgets():
        if isinstance(widget, QMainWindow):
            return widget
    return None

def show_palette(name: str, placeholder: str, actions: List[Action],
                close_key: str, func: Callable) -> None:
    def create_palette():
        global g_current_widget
        g_current_widget = CommandPalette(get_main_window())
        g_current_widget.setAttribute(Qt.WA_DeleteOnClose)
        g_current_widget.show(name, placeholder, actions, close_key, func)

    # post_to_thread(create_palette)
    # post_to_timer(create_palette, 100)
    create_palette()

def cleanup_palettes() -> None:
    # Note: Python doesn't have direct equivalent of Q_CLEANUP_RESOURCE
    # This would need to be handled differently depending on resource management approach
    pass

def set_path_handler(handler: Callable) -> None:
    global pluginPath
    pluginPath = handler
