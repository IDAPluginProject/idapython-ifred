from PySide6.QtCore import QFileSystemWatcher, QDir, QFile, QIODevice
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import json as json_lib
from typing import Callable, Optional

static_updated = False
from . import api

def load_file_from_bundle(filename: str, file: QFile, updated: bool) -> str:
    resource_initialized = False

    if not resource_initialized:
        # Initialize Qt resource system
        # Note: Q_INIT_RESOURCE needs to be handled differently in Python
        # This is typically done through pyrcc tool or QResource.registerResource()
        resource_initialized = True
        QDir.addSearchPath("theme", api.pluginPath("theme/"))

    res_file = QFile(f":/bundle/{filename}")
    updated = False

    if res_file.exists():
        if not res_file.open(QIODevice.ReadOnly):
            return ""

        bytes_data = res_file.readAll()
        content = str(bytes_data.data(), 'utf-8')

        dir_path = QDir(file.fileName())
        dir_path.mkpath("..")

        if file.open(QIODevice.WriteOnly):
            file.write(bytes_data)
            file.close()

        updated = True
        return content
    else:
        return ""

def loadFile(filename: str, force_update: bool = False, updated: bool = static_updated) -> str:
    absolute_path = api.pluginPath(filename)
    file = QFile(absolute_path)

    updated = False

    if not file.exists():
        # Check if it exists in bundle resource
        return load_file_from_bundle(filename, file, updated)

    if not file.open(QIODevice.ReadOnly):
        return ""

    content = str(file.readAll().data(), 'utf-8')
    updated = True

    return content

# Cache for JSON documents
cached_json = {}

def load_json(filename: str, force_update: bool = False) -> dict:
    updated = False
    content_str = loadFile(filename, force_update, updated)

    if not updated:
        return cached_json.get(filename, {})

    try:
        json_data = json_lib.loads(content_str)
        cached_json[filename] = json_data
        return json_data
    except json_lib.JSONDecodeError:
        return {}
