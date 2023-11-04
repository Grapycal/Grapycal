from grapycal.sobjects.controls.control import Control
from objectsync import StringTopic, IntTopic, ListTopic


class ThreeControl(Control):
    '''
    '''
    frontend_type = 'ThreeControl'
    def build(self):
        super().build()
        self.points = self.add_attribute('points',ListTopic,is_stateful=False)
        self.lines = self.add_attribute('lines',ListTopic,is_stateful=False)