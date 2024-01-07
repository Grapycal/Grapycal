from grapycal.sobjects.controls.control import Control
from objectsync import StringTopic, IntTopic


class TextControl(Control):
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