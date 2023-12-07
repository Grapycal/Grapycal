Examples of Node Definition
================================

PrintNode
-----------

A simple node that displays the data received from the input edge.

.. code-block:: python

    class PrintNode(Node):
        '''
        Display the data received from the input edge.
    
        :inputs:
            - data: data to be displayed
    
        '''
        category = 'interaction'
    
        def build_node(self):
            self.add_in_port('',max_edges=1)
            self.text_control = self.add_control(TextControl, readonly=True)
            self.label.set('Print')
            self.shape.set('simple')
            self.css_classes.append('fit-content')
    
        def edge_activated(self, edge, port):
            '''
            Called when some data is received from the input edge.
            '''

            # tell user that the node is running
            self.flash_running_indicator()

            # get the data from the edge
            data = edge.get_data()

            # display the data
            self.text_control.text.set(str(data))
    
        def input_edge_added(self, edge: Edge, port: InputPort):
            if edge.is_data_ready():
                self.flash_running_indicator()
                data = edge.get_data()
                self.text_control.text.set(str(data))
    
        def input_edge_removed(self, edge: Edge, port: InputPort):
            self.text_control.text.set('')

CatNode
-------

A node that concatenates all torch tensors received from the input edges.

.. code-block:: python

    class CatNode(FunctionNode):
        category = 'torch/operations'
        def build_node(self):
            self.label.set('🐱0')
            self.shape.set('round')
            self.dim = self.add_attribute('dim',IntTopic,0,editor_type='int')
            self.add_in_port('inputs')
            self.add_out_port('out')
        
        def init_node(self):
            self.dim.on_set.add_manual(self.dim_changed)
            if self.is_new:
                self.dim.set(0)
    
        def restore_from_version(self, version: str, old: NodeInfo):
            super().restore_from_version(version, old)
            self.restore_attributes('dim')
    
        def dim_changed(self,dim):
            self.label.set('🐱'+str(dim))
        
        def calculate(self, inputs: list[Any]):
            return torch.cat(inputs,dim=self.dim.get())

ZeroesNode
----------

A node that outputs a tensor of zeros.

.. code-block:: python

    class ZeroesNode(SourceNode):
        category = 'torch/generative'
        def build_node(self):
            super().build_node()
            self.shape.set('simple')
            self.label.set('Zeroes')
            self.out = self.add_out_port('tensor')
            self.shape_text = self.add_control(TextControl,'shape_text')
            self.shape_text.text.set('2,2')
            self.shape_text.label.set('Shape')
            self.device = self.add_attribute('device',StringTopic,'cpu',editor_type='text')
    
        def restore_from_version(self, version: str, old: NodeInfo):
            super().restore_from_version(version, old)
            self.restore_controls('shape_text')
            self.restore_attributes('device')
    
        def task(self):
            self.out.push_data(torch.zeros(*map(int, self.shape_text.text.get().split(',')),device=self.device.get()))
    