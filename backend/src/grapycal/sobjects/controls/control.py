from grapycal.extension.utils import ControlInfo
from objectsync import SObject

import abc
from typing import Callable, Generic, TypeVar

class Control(SObject):
    '''
    A control enables the user to interact with a node via the GUI. There are different types of controls, such as a text input control
    a slider control, a checkbox control, etc. Controls can be added to a node during the Node.build() process or dynamically added or removed at runtime.
    '''
    def restore_from(self,old:ControlInfo):
        '''
        Default recovery process. If the control class get updated in Grapycal, override this method to customize the recovery process
        for different Grapycal versions.
        '''
        for k,v in old.attributes.items():
            if self.has_attribute(k):
                self.get_attribute(k).set(v)

T = TypeVar('T')
class ValuedControl(abc.ABC, Control, Generic[T]):
    @abc.abstractmethod
    def get_value(self) -> T:
        pass

    @abc.abstractmethod
    def value_ready(self) -> bool:
        pass

    @abc.abstractmethod
    def set_activation_callback(self, callback:Callable[[],None]):
        '''
        By invoking the callback, the control notifies the node for events such as a button click, a text change, etc.
        The callback invokes node.on_edge_activated() method.
        '''
        pass

    def take_label(self, label) -> bool:
        '''
        If the control takes the responsibility of displaying the label of the port,
        return True. Otherwise, return False.
        '''
        return False
         
    def set_with_value_from_edge(self, value):
        '''
        Set the value of the control with the value from the edge.
        The control can implement this method if it want to update its value as some data from edge flows into the port.
        Raise an exception if the value is not valid. It will be caught by the port and displayed to the user.
        '''
        pass