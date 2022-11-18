from typing import Callable, Dict, Optional

from nicegui import ui

from ..element import Element
from ..events import ValueChangeEventArguments, handle_event
from .color_picker import ColorPicker
from .mixins.value_element import ValueElement


class ColorInput(ValueElement):

    def __init__(self, label: str = None, *,
                 placeholder: str = None, value: str = '', on_change: Optional[Callable] = None) -> None:
        """Color Input

        :param label: displayed label for the color input
        :param placeholder: text to show if no color is selected
        :param value: the current color value
        :param on_change: callback to execute when the input is confirmed by leaving the focus
        """
        super().__init__(tag='q-input', value=value, on_value_change=on_change)
        self._props['label'] = label
        self._props['placeholder'] = placeholder

        with self.add_slot('append'):
            self.picker = ColorPicker(on_pick=lambda e: self.set_value(e.color))
            self.button = ui.button(on_click=self.picker.open) \
                .props('icon=colorize flat round', remove='color').classes('cursor-pointer')
