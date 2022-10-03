from typing import Any, Callable, Dict, List, Optional, Union

import justpy as jp

from .choice_element import ChoiceElement


class Select(ChoiceElement):

    def __init__(self, options: Union[List, Dict], *,
                 label: Optional[str] = None, value: Any = None, on_change: Optional[Callable] = None):
        """Dropdown Selection

        :param options: a list ['value1', ...] or dictionary `{'value1':'label1', ...}` specifying the options
        :param value: the initial value
        :param on_change: callback to execute when selection changes
        """
        view = jp.QSelect(options=options, label=label, input=self.handle_change, temp=False)

        super().__init__(view, options, value=value, on_change=on_change)

    def value_to_view(self, value: Any):
        if isinstance(value, list):
            value = tuple(value)
        matches = [o for o in self.view.options if o['value'] == value]
        if any(matches):
            return matches[0]['label']
        else:
            return value

    def handle_change(self, msg: Dict):
        msg['label'] = msg['value']['label']
        msg['value'] = msg['value']['value']
        if isinstance(self.view.options[0]['value'], tuple) and isinstance(msg['value'], list):
            msg['value'] = tuple(msg['value'])
        return super().handle_change(msg)
