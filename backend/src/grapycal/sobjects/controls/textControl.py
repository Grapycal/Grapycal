from enum import Enum
from grapycal.sobjects.controls.control import ValuedControl
from grapycal.utils.misc import Action
from objectsync import EventTopic, StringTopic, IntTopic


class TextControl(ValuedControl[str]):
    '''
    To add a text control to a node, use the following code in the node:
    ```python
    self.add_control(TextControl, text='', label='', editable=True)
    ```
    '''

    class ActivationMode(Enum):
        ON_CHANGE = 0
        ON_FINISH = 1
        NO_ACTIVATION = 2

        def __eq__(self, __value: object) -> bool:
            return self.value == __value

    frontend_type = 'TextControl'
    def build(self, text:str='', label:str='',readonly=False, editable:bool=True, placeholder:str='', activation_mode:ActivationMode=ActivationMode.ON_FINISH):
        if readonly:
            editable = False
        self.text = self.add_attribute('text', StringTopic, text, is_stateful= not readonly, order_strict= not readonly)
        self.label = self.add_attribute('label', StringTopic, label)
        self.editable = self.add_attribute('editable', IntTopic, 1 if editable else 0)
        self.placeholder = self.add_attribute('placeholder', StringTopic, placeholder)
        self.activation_mode = self.add_attribute('activation_mode', IntTopic, activation_mode.value)

    def init(self):
        super().init()
        self.on_finish = Action()
        self.register_service('finish', self.on_finish.invoke)

    def set(self, text:str):
        self.text.set(text)

    def get(self) -> str:
        return self.text.get()

    def value_ready(self) -> bool:
        return True
    
    def set_activation_callback(self, callback):
        if self.activation_mode.get() == TextControl.ActivationMode.ON_CHANGE:
            self.text.on_set += callback

        elif self.activation_mode.get() == TextControl.ActivationMode.ON_FINISH:
            self.on_finish += callback

        elif self.activation_mode.get() == TextControl.ActivationMode.NO_ACTIVATION:
            pass

        else:
            raise ValueError()

    def take_label(self, label) -> bool:
        if self.label.get() == '':
            self.label.set(label)
            return True
        return False
    
    def set_with_value_from_edge(self, value):
        self.set(str(value)) # TODO find more proper way to handle this
