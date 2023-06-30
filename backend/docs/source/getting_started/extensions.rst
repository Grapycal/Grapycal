Extensions
================

Each extension defines a set of nodes that can be used in a Grapycal workspace. The extension `builtin_nodes` is automatically included in 
every workspace, providing a set of basic nodes. You can create your own extensions to define custom nodes and import them in your workspace.


Create an Extension
-------------------

Let's create an extension named `grapycal_myext` that defines a node named `IsEvenNode`.

1. In ``working_dir``, create a directory named `grapycal_myext`.

.. note:: The extension folder must be placed in the working directory of the workspace and must start with `grapycal_` to 
    be discovered by Grapycal.

2. In `grapycal_myext`, create a file named `__init__.py` with the following content:

.. code-block:: python

    from grapycal import Node

    class IsEvenNode(Node):
        category = 'function'
        def build(self):
            self.label.set('IsEven')
            self.add_in_port('number')
            self.add_out_port('isEven')

The extension is now ready to be imported in a workspace. 

3. Go to the web interface and click on the `Settings` button.
You should see the extension in the list of available extensions. Right click on it and select `Import to workspace`.

.. image:: https://i.imgur.com/pQu7ZSQ.png
    :align: center
    :width: 80%

4. Yaay! The `IsEvenNode` is now available in your workspace. 

.. image:: https://i.imgur.com/foOsZY7.png
    :align: center
    :width: 80%

It doesn't actually do anything, but it's a start. Let's add some logic to it.

Edit the Extension
------------------

Grapycal supports hot reloading of extensions. This means that you can edit the extension code and see the changes in the workspace without having to restart the server.

1. Edit the `__init__.py` and add some logic to the `edge_activated` method:

.. code-block:: python

    from grapycal import Node, Edge, InputPort

    class IsEvenNode(Node):
        category = 'function'
        def build(self):
            self.label.set('IsEven')
            self.add_in_port('number')
            self.out_port = self.add_out_port('isEven')

        def edge_activated(self, edge: Edge, port: InputPort):

            # Compute the result
            result = edge.get_data() % 2 == 0

            # Feed the result to each edge connected to the output port
            for e in self.out_port.edges:
                e.push_data(result)

2. Go back to the web interface, right click on the extension card, and select `Reload`.

The node should now work as expected.

.. image:: https://i.imgur.com/tQDv9th.png
    :align: center
    :width: 80%

.. note:: Don't forget to double click on EvalNodes!