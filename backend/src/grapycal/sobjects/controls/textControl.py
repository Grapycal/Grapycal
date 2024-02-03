from grapycal.sobjects.controls.control import ValuedControl
from objectsync import StringTopic, IntTopic


class TextControl(ValuedControl[str]):
    '''
    To add a text control to a node, use the following code in the node:
    ```python
    self.add_control(TextControl, text='', label='', editable=True)
    ```
    '''

    frontend_type = 'TextControl'
    def build(self, text:str='', label:str='',readonly=False, editable:bool=True, placeholder:str=''):
        if readonly:
            editable = False
        self.text = self.add_attribute('text', StringTopic, text, is_stateful= not readonly, order_strict= not readonly)
        self.label = self.add_attribute('label', StringTopic, label)
        self.editable = self.add_attribute('editable', IntTopic, 1 if editable else 0)
        self.placeholder = self.add_attribute('placeholder', StringTopic, placeholder)
    
    def set(self, text:str):
        self.text.set(text)

    def get(self):
        return self.text.get()

    def get_value(self) -> str:
        return self.get()

    def value_ready(self) -> bool:
        return True
    
    def set_activation_callback(self, callback):
        self.activation_callback = callback

    def take_label(self, label) -> bool:
        if self.label.get() == '':
            # if self.placeholder.get() == '':
            #     self.placeholder.set(label)
            #     return True
            # else:
                self.label.set(label)
                return True
        return False
