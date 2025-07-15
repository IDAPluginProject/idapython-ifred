from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtWidgets import QStyle

from .filter import PaletteFilter
from .utils import loadFile

class ItemDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)
        self.document = QTextDocument(self)
        self.recents = 0
        self.style_updated = False
        self.cached_size = QSize()
        self.updateCSS(loadFile("theme/window.css"))

    def updateCSS(self, style_sheet):
        self.document.setDefaultStyleSheet(style_sheet)
        text_option = QTextOption()
        text_option.setWrapMode(QTextOption.WrapMode.WrapAnywhere)
        self.document.setDefaultTextOption(text_option)
        self.document.setDocumentMargin(0)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        super().paint(painter, option, index)

        try:
            class_name_map = {
                QStyle.StateFlag.State_None: "none",
                QStyle.StateFlag.State_Selected: "selected",
                QStyle.StateFlag.State_MouseOver: "hover",
                QStyle.StateFlag.State_Selected | QStyle.State_MouseOver: "selected hover"
            }

            opt = QStyleOptionViewItem(option)
            self.initStyleOption(opt, index)

            action = index.data()
            keyword = index.data(Qt.ItemDataRole.UserRole)

            painter.save()

            widget = option.widget
            style = widget.style()

            if index.row() == self.recents - 1:
                opt.state |= QStyle.StateFlag.State_On

            opt.text = ""
            opt.state &= ~QStyle.StateFlag.State_HasFocus
            opt.state |= QStyle.StateFlag.State_Active
            style.drawControl(QStyle.CE_ItemViewItem, opt, painter, widget)

            painter.restore()

            painter.save()

            text_rect = style.subElementRect(QStyle.SE_ItemViewItemText, option, widget)
            painter.translate(text_rect.left(), text_rect.top())

            if text_rect.top() >= 0:
                text_rect = text_rect.intersected(widget.contentsRect())

            document = self.renderAction(
                False,
                class_name_map[opt.state & (QStyle.StateFlag.State_Selected | QStyle.StateFlag.State_MouseOver)],
                keyword,
                action
            )

            document.drawContents(painter, QRectF(0, 0, text_rect.width(), text_rect.height()))
            painter.restore()
        except Exception as e:
            print('== Exception 2222')
            print(type(e))
            print(e)

    def sizeHint(self, option, index):
        action = index.data()
        document = self.renderAction(True, "", "", action)
        document.setTextWidth(option.rect.width())
        return QSize(option.rect.width(), int(document.size().height()))

    def renderAction(self, size_hint, class_name, keyword, action):
        html = f'<table width=100% cellpadding=0 cellspacing=0 class="{class_name}"><tr><td class="name">'
        html += self.highlight(keyword, action.name) if not size_hint else "keyword"
        html += "</td>"

        if action.shortcut:
            html += f'<td width=50px class="shortcut" align="right">{action.shortcut}</td>'

        html += "</tr>"

        if action.description:
            html += f'<tr><td class="description" colspan=2>{action.description}</td></tr>'

        html += "</table>"
        self.document.setHtml(html)
        return self.document

    def setRecents(self, index):
        self.recents = index

    @staticmethod
    def escape(text):
        return text.replace("<", "&lt;")

    def highlight(self, needle, haystack):
        em = "<em>"
        em_end = "</em>"
        highlights = []

        if needle:
            pos = -1
            last_pos = 0
            for c in needle:
                pos = haystack.lower().find(c.lower(), pos + 1)
                if pos == -1:
                    break

                highlights.append(self.escape(haystack[last_pos:pos]))
                highlights.append(em)
                highlights.append(self.escape(haystack[pos]))
                highlights.append(em_end)
                last_pos = pos + 1

            highlights.append(haystack[last_pos:])
        else:
            highlights.append(self.escape(haystack))

        return "".join(highlights)


class PaletteItems(QListView):
    def __init__(self, parent, palette_name, search_service):
        super().__init__(parent)
        self.model_ = PaletteFilter(self, palette_name, search_service)
        self.item_delegate_ = ItemDelegate(self)

        # Optimization
        self.setUniformItemSizes(True)
        self.setLineWidth(0)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        self.setModel(self.model_)
        self.setItemDelegate(self.item_delegate_)

        self.model_.filteringDone.connect(self._on_filtering_done)

    def _on_filtering_done(self, index):
        self.item_delegate_.setRecents(index)
        self.setCurrentIndex(self.model_.index(0, 0))

    def model(self):
        return self.model_

    def __del__(self):
        del self.model_
