import re
from grapycal.sobjects.node import Node
from grapycal import ListTopic, Edge, InputPort, ButtonControl


class ProcedureNode(Node):
    category = 'procedural'

    def build_node(self):
        self.in_port = self.add_in_port('',1)
        self.label.set('Procedure')
        self.shape.set('normal')
        self.steps = self.add_attribute('steps', ListTopic, editor_type='list')
        self.add_btn = self.add_control(ButtonControl)
        self.add_btn.label.set('+')
        self.add_btn.on_click.add_auto(self.add_pressed)

    def init_node(self):
        self.steps.add_validator(ListTopic.unique_validator)
        self.steps.on_insert.add_auto(self.add_step)
        self.steps.on_pop.add_auto(self.remove_step)
        if self.is_new:
            self.steps.insert('1')

    def add_pressed(self):
        new_step = 0
        for step in self.steps:
            if re.match(r'[0-9]+', step):
                new_step = max(new_step, int(step))
        new_step += 1
        self.steps.insert(str(new_step))

    def add_step(self, step, position):
        self.add_out_port(step)

    def remove_step(self, step, position):
        self.remove_out_port(step)

    def edge_activated(self, edge: Edge, port: InputPort):
        self.run(self.task)

    def input_edge_added(self, edge: Edge, port: InputPort):
        self.run(self.task)

    def task(self):
        self.iterator = iter(self.steps.get()) #type: ignore
        self.run(self.next)
        
    def next(self):
        try:
            step = next(self.iterator) #type: ignore
        except StopIteration:
            return
        port = self.get_out_port(step)
        port.push_data()
        self.run(self.next,to_queue=False)