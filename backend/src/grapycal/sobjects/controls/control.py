from grapycal.extension.utils import ControlInfo
from objectsync import SObject

class Control(SObject):
    '''
    A control enables the user to interact with a node via the GUI. There are different types of controls, such as a text input control
    a slider control, a checkbox control, etc. Controls can be added to a node during the Node.build() process or dynamically added or removed at runtime.
    '''
    def recover_from(self,old:ControlInfo):
        '''
        Default recovery process. If the control class get updated in Grapycal, override this method to customize the recovery process
        for different Grapycal versions.
        '''
        for k,v in old.attributes.items():
            self.get_attribute(k).set(v)
        
         