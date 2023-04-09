from __future__ import annotations

from typing import Callable, Optional

from nicegui import ui

dragged: Optional[card] = None


class column(ui.column):

    def __init__(self, name: str, on_drop: Callable = None) -> None:
        super().__init__()
        with self.classes('bg-grey-5 w-60 p-4 rounded shadow-2'):
            ui.label(name).classes('text-bold ml-1')
        self.on('dragover.prevent', self.highlight)
        self.on('dragleave', self.unhighlight)
        self.on('drop', self.move_card)
        self.on_drop = on_drop

    def highlight(self) -> None:
        self.classes(add='bg-grey-2')

    def unhighlight(self) -> None:
        self.classes(remove='bg-grey-2')

    def move_card(self) -> None:
        global dragged
        self.unhighlight()
        dragged.parent_slot.parent.remove(dragged)
        with self:
            card(dragged.text)
        self.on_drop(dragged)
        dragged = None


class card(ui.card):

    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text
        with self.props('draggable').classes('w-full cursor-pointer bg-grey-1'):
            ui.label(self.text)
        self.on('dragstart', self.handle_dragstart)

    def handle_dragstart(self) -> None:
        global dragged
        dragged = self
