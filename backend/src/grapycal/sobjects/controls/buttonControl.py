from typing import Any, Dict
from grapycal.sobjects.controls.control import Control
from objectsync import SObject, StringTopic, IntTopic, ListTopic, ObjListTopic, GenericTopic, FloatTopic, EventTopic


class ButtonControl(Control):
    '''
    To add a button control to a node, use the following code in the node:
    ```python
    self.add_control(Button, label='')
    ```
    '''
    frontend_type = 'ButtonControl'
    def pre_build(self, attribute_values: Dict[str, Any] | None,label='', **_):
        super().pre_build(attribute_values, **_)
        self.label = self.add_attribute('label', StringTopic, label)
        self._click = self.add_attribute('click', EventTopic, is_stateful=False)
        self.on_click = self._click.on_emit
        