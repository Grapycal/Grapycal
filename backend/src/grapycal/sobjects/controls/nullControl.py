from grapycal.sobjects.controls.control import ValuedControl, T


class NullControl(ValuedControl):
    def get_value(self) -> T:
        raise Exception('Data not available')

    def value_ready(self) -> bool:
        return False