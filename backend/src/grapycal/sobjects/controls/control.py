from grapycal.extension.utils import ControlInfo
from objectsync import SObject

import abc
from typing import Generic, TypeVar

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
         