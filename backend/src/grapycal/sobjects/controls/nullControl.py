from grapycal.sobjects.controls.control import ValuedControl


class NullControl(ValuedControl):
    def get_value(self):
        raise Exception('Data not available')

    def value_ready(self) -> bool:
        return False
    
    def set_activation_callback(self, callback):
        pass