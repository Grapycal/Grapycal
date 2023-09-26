
This is a detailed guide on how to define a node and some related knowledges.

Life Cycle of a Node
========================




Define a Node
======================


A new type of node is created by inheriting from the `Node` class. A minimal node definition looks like this:

.. code-block:: python

    class CounterNode(Node):
        category = 'function'
        def build_node(self):
            self.text = self.add_control(TextControl)
            self.text.text.set('0')
            self.add_control(ButtonControl, label='Add').on_click += self.button_clicked
            self.add_in_port('set')
            self.add_out_port('get')
    
        def init_node(self):
            self.i=0
    
        def button_clicked(self):
            self.i += 1
            self.text.text.set(str(self.i))