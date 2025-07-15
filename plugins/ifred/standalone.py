import os, sys
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtWidgets import QApplication
import random
import string
import threading

basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.abspath(basedir + "/../"))
from ifred.CommandPalette import CommandPalette
from ifred.filter import SearchService
from ifred.api import set_path_handler
from ifred.action import Action

COUNT = 500000
COUNT = 500

def random_key():
    keys = ["Shift"]
    return random.choice(keys)

def test_items(count=COUNT):
    action_list = []
    action_list.append(Action(
        id="std::runtime_error",
        name="raise exception!!",
        shortcut="",
        description="Just raises an exception"
    ))

    for i in range(count):
        # Simulate complex random ID generation similar to C++ version
        rand_num = random.getrandbits(64)
        id_str = f"{rand_num:x}:{i}"

        action_list.append(Action(
            id=id_str,
            name=id_str + id_str,
            shortcut=f"{random_key()}+{i % 10}",
            description=f"{i}th element"
        ))

    return action_list

class CustomService(SearchService):
    start_searching = Signal(str)
    done_searching = Signal(str, list, int)

    def __init__(self):
        super().__init__(None)
        self.items = test_items(500)
        self.start_searching.connect(self.on_search)

    def on_search(self, keyword):
        # Shuffle items
        items_copy = self.items.copy()
        random.shuffle(items_copy)
        self.done_searching.emit(keyword, items_copy, 0)
        self.done_searching.emit(
            keyword,
            [{"id": "install", "name": "Press ENTER to install your extension."}],
            0
        )

    def cancel(self):
        pass

    def runInSeparateThread(self) -> bool:
        return False

def TestPluginPath(name):
    return f"{basedir}/res/{name}"

def main():
    app = QApplication([])
    # Assuming set_path_handler is defined elsewhere
    set_path_handler(TestPluginPath)
    QApplication.setQuitOnLastWindowClosed(True)

    palette = CommandPalette()  # Assuming CommandPalette is defined elsewhere
    palette.setWindowFlags(Qt.Tool)
    palette.setAttribute(Qt.WA_TranslucentBackground, False)
    # palette.setAttribute(Qt.WA_DeleteOnClose, True)

    def action_handler(action):
        import traceback
        traceback.print_stack()
        if action.id == "std::runtime_error":
            raise RuntimeError("raised!")
        print(f"Action: {action.id} {action.name} {action.shortcut}")
        return False

    palette.show("<test palette>", "Enter item name...", test_items(),
                "Ctrl+P", action_handler)
    # palette.show("<test palette>", "Enter item name...", CustomService(),
    #             "Ctrl+P", action_handler)

    app.exec()

if __name__ == "__main__":
    main()
