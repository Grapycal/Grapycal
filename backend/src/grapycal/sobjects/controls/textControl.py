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
    def build(self, text:str='', label:str='',readonly=False, editable:bool=True):
        if readonly:
            editable = False
        self.text = self.add_attribute('text', StringTopic, text, is_stateful= not readonly)
        self.label = self.add_attribute('label', StringTopic, label)
        self.editable = self.add_attribute('editable', IntTopic, 1 if editable else 0)
        