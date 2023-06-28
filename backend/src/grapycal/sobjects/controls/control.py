from objectsync import SObject, StringTopic, IntTopic, ListTopic, ObjListTopic, GenericTopic, FloatTopic

class Control(SObject):
    '''
    A control enables the user to interact with a node via the GUI. There are different types of controls, such as a text input control
      a slider control, a checkbox control, etc. Controls can be added to a node during the Node.build() process or dynamically added or removed at runtime.
    '''
    pass