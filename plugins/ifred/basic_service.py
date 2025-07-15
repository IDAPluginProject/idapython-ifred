from .qt_bindings import *
from typing import List, Dict, Tuple, Optional
from rapidfuzz import fuzz

from .action import Action
from .filter import SearchService
from . import fts_fuzzy_match

class CanceledError(Exception):
    pass

MAX_RECENT_ITEMS = 100
SAME_THREAD_THRESHOLD = 20000

distances: Dict[Tuple[str, str], int] = {}
def distance(s1: str, s2: str) -> int:
    # distances = QThreadStorage[Dict[Tuple[str, str], int]]()
    pair = (s1, s2)

    # if not distances.hasLocalData():
    #     distances.setLocalData({})

    # distances_map = distances.localData()
    distances_map = distances
    if pair in distances_map:
        return distances_map[pair]

    score = 0
    score = fuzz.ratio(s1, s2)

    distances_map[pair] = -score
    return -score

def convert_variant(a) -> int:
    return int(a)

def convert_int(a: int) -> int:
    return a

def convert_hash(source: Dict[str, any], target_type) -> Dict[str, any]:
    return {k: convert_variant(v) if target_type == any else convert_int(v)
            for k, v in source.items()}

class BasicService(SearchService):
    def __init__(self, parent: QObject, palette_name: str, actions: List[Action]):
        super().__init__(parent)
        self.actions = actions
        self.storage = QSettings("ifred", palette_name)
        self.indexes = [0] * len(actions)
        self.recent_indexes = []
        self.recent_actions = {}
        self.canceled = False

        self.startSearching.connect(self.search)
        self.itemClicked.connect(self._handle_item_clicked)

        self.storage.sync()
        recent_actions_variant = self.storage.value("recent_actions", {})
        self.recent_actions = convert_hash(recent_actions_variant, int)
        self.recent_indexes = [0] * len(self.recent_actions)

    def _handle_item_clicked(self, id: str):
        to_remove = []
        for key in self.recent_actions:
            self.recent_actions[key] += 1
            if self.recent_actions[key] >= MAX_RECENT_ITEMS:
                to_remove.append(key)

        for key in to_remove:
            del self.recent_actions[key]

        self.recent_actions[id] = 0
        self.storage.setValue("recent_actions",
                            convert_hash(self.recent_actions, any))
        self.storage.sync()

    def runInSeparateThread(self) -> bool:
        return len(self.actions) >= SAME_THREAD_THRESHOLD

    def cancel(self):
        self.canceled = True

    def search(self, keyword: str):
        nonrecent_count = 0
        recent_count = 0
        recent_actions = dict(self.recent_actions)

        self.canceled = False

        for i in range(len(self.indexes)):
            if self.canceled:
                return
            if not keyword or fts_fuzzy_match.fuzzy_match_simple(keyword, self.actions[i].name):
                if self.actions[i].id in recent_actions:
                    self.recent_indexes[recent_count] = i
                    recent_count += 1
                else:
                    self.indexes[nonrecent_count] = i
                    nonrecent_count += 1

        try:
            def recent_sort_key(idx):
                if self.canceled:
                    raise CanceledError()
                return recent_actions[self.actions[idx].id]

            self.recent_indexes[:recent_count] = sorted(
                self.recent_indexes[:recent_count],
                key=recent_sort_key
            )

            if len(keyword) > 1:
                def distance_sort_key(idx):
                    if self.canceled:
                        raise CanceledError()
                    return distance(keyword, self.actions[idx].name)

                self.indexes[:nonrecent_count] = sorted(
                    self.indexes[:nonrecent_count],
                    key=distance_sort_key
                )

        except CanceledError:
            return

        result = []
        for i in range(recent_count):
            result.append(self.actions[self.recent_indexes[i]])

        for i in range(nonrecent_count):
            result.append(self.actions[self.indexes[i]])

        self.doneSearching.emit(keyword, result, recent_count)
