Extension
================

Nodes in Grapycal are provided by extensions. An extension is a Python package that
defines a set of nodes for a specific domain. For example, there would be an extension for image processing, another one for
deep learning, etc.
The extension `grapycal_builtin` is automatically included in every workspace, providing a set of basic nodes. You can create your own extensions to define custom nodes doing arbitrary tasks.

Here is a brief walkthrough of how to create an extension. For more details about defining nodes, see Contribution Guide: :doc:`../contribution_guide/define_a_node`.

Create an Extension
-------------------

Let's create an extension named `grapycal_myext` that defines a node named `IsEvenNode`.

1. In the working directory (the one where you run ``grapycal``), create a directory named ``grapycal_myext``.

.. note:: The extension folder must be placed in the working directory and must start with ``grapycal_`` to
    be discovered by Grapycal.

2. In ``grapycal_myext``, create ``__init__.py`` with the following content:

.. code-block:: python

    from grapycal import Node

    class IsEvenNode(Node):
        category = 'function'
        def build_node(self):
            self.label.set('IsEven')
            self.add_in_port('number')
            self.add_out_port('isEven')

The extension is now ready to be imported in a workspace.

3. Go to the GUI and click on the `Extensions 🚀` button in the right.
You should see the extension in the list of available extensions. Click on the `+` button to import it.

.. image:: https://i.imgur.com/sT18b7h.png
    :align: center
    :width: 80%

4. Yay! The `IsEvenNode` is now available in your workspace.

.. image:: https://i.imgur.com/foOsZY7.png
    :align: center
    :width: 80%

The node is just a layout now. Let's add some logic to it.

Edit the Extension
------------------

Grapycal supports hot reloading of extensions i.e. you can edit the extension code and see the changes in the workspace without having to restart the server.

1. Edit the `__init__.py` and add some logic to the `edge_activated` method:

.. code-block:: python

    from grapycal import Node, Edge, InputPort

    class IsEvenNode(Node):
        category = 'function'
        def build_node(self):
            self.label.set('IsEven')
            self.add_in_port('number')
            self.out_port = self.add_out_port('isEven')

        def edge_activated(self, edge: Edge, port: InputPort):

            # Compute the result
            result = edge.get_data() % 2 == 0

            # Feed the result to each edge connected to the output port
            for e in self.out_port.edges:
                e.push_data(result)

2. Go back to the GUI, right click on the extension card, and select `Reload ↻`

The node should now work as expected.

.. image:: https://i.imgur.com/tQDv9th.png
    :align: center
    :width: 80%

.. note:: Don't forget to double click on EvalNodes to update their output value.

For more details about the API for defining nodes, see Contribution Guide: :doc:`../contribution_guide/define_a_node`.
