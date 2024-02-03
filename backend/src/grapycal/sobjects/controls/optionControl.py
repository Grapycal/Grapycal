from grapycal.sobjects.controls.control import ValuedControl
from objectsync import ListTopic, StringTopic, IntTopic


class OptionControl(ValuedControl[str]):
    '''
    To add a option control to a node, use the following code in the node:
    ```python
    self.add_control(OptionControl, value='apple', options=['apple','orange'], label='pick a fruit')
    ```
    '''

    frontend_type = 'OptionControl'
    def build(self, value:str='', options:list[str]=[], label:str=''): 
        self.value = self.add_attribute('value',StringTopic,value)
        self.options = self.add_attribute('options',ListTopic,options)
        self.label = self.add_attribute('label',StringTopic,label)

    def init(self):
        self.on_set = self.value.on_set
    
    def set(self, value:str):
        self.value.set(value)

    def get(self):
        return self.value.get()

    def get_value(self) -> str:
        return self.get()

    def value_ready(self) -> bool:
        return True
    
    def set_activation_callback(self, callback):
        self.value.on_set += callback

    def take_label(self, label) -> bool:
        if self.label.get() == '':
            self.label.set(label)
            return True
        return False
    
    def set_with_value_from_edge(self, value):
        assert value in self.options.get(), f'Value {value} is not a valid option'
        if value != self.value.get():
            self.set(value)