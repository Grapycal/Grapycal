from grapycal.sobjects.controls.control import Control
from objectsync import StringTopic, IntTopic, ListTopic, SetTopic, DictTopic, EventTopic


class LinePlotControl(Control):
    '''
    '''
    frontend_type = 'LinePlotControl'
    def build(self):
        super().build()
        self.lines = self.add_attribute('lines',ListTopic)
        self.add_points_topic = self.add_attribute('add_points',EventTopic,is_stateful=False,order_strict=True)
        self.clear_topic = self.add_attribute('clear',EventTopic,is_stateful=False,order_strict=True)

    def add_points(self, name, xs, ys):
        if not isinstance(xs, list):
            xs = [xs]
        if not isinstance(ys, list):
            ys = [ys]
            
        if len(xs) != len(ys):
            raise ValueError('xs and ys must have the same length')
        
        self.add_points_topic.emit(name=name,xs=xs,ys=ys)

    def clear(self, name):
        self.clear_topic.emit(name=name)

    def clear_all(self):
        for line in self.lines:
            self.clear(line)