from typing import Any, Dict
from grapycal.sobjects.controls.control import ValuedControl
from objectsync import StringTopic, EventTopic


class ButtonControl(ValuedControl[None]):
    '''
    To add a button control to a node, use the following code in the node:
    ```python
    self.add_control(Button, label='')
    ```
    '''
    frontend_type = 'ButtonControl'
    def build(self, label:str=''):
        self.label = self.add_attribute('label', StringTopic, label, is_stateful=False)
        self._click = self.add_attribute('click', EventTopic, is_stateful=False)
        
    def init(self):
        self.on_click = self._click.on_emit
    def set_activation_callback(self, callback):
        self.on_click += callback
    
    def get_value(self) -> None:
        return None
    
    def value_ready(self) -> bool:
        return True