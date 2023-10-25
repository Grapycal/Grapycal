Define a Node Type: The Low-Level Way
======================

This guide provides a comprehensive explanation of how to define a node type directly from ``Node`` class.

Specify the Category
-------------------------

The category is used to group nodes in the node list. For example:

.. code-block:: python

    class CounterNode(Node):
        category = 'demo'

.. _build_node:

``build_node()``
-------------------------
The ``build_node()`` method is called once when a node is created. This is where you define the structure of the node, including      :doc:`controls`,
:doc:`port`,
and Attributes.
Here's an example:

.. code-block:: python

    class CounterNode(Node):
        category = 'demo'
    
        def build_node(self):
            self.text = self.add_text_control('0')
            self.button = self.add_button_control('Add')

The above code results in a node with a text field and a button, as shown below:

.. image:: https://i.imgur.com/omyQjak.png
   :width: 300px

Things you can do in ``build_node()``:

-  ``self.add_text_control``: Add a :ref:`developer_guide/controls:text control` to the node.
-  ``self.add_button_control`` : Add a :ref:`developer_guide/controls:button control` to the node.
-  ``self.add_image_control`` : Add an :ref:`developer_guide/controls:image control` to the node.
-  ``self.add_in_port`` : Add an :ref:`developer_guide/port:port` to the node.
-  ``self.add_out_port`` : Add an :ref:`developer_guide/port:port` to the node.
-  ``self.add_attribute`` : Add an :ref:`developer_guide/attribute:attribute` to the node.
-  ``self.expose_attribute`` : Expose an attribute to the inspector panel.
-  Set values of the node's attributes to customize the node's appearance.
    *   ``self.shape``: can be ``'normal'``, ``'simple'``, or ``'round'``.
    *   ``self.label``: the node's label.
    *   ``self.label_offset``: the offset of the label from the node's center.



``init_node()``
-------------------------

The ``init_node()`` method is called every time a node object is instantiated. It's used for initialization tasks other than adding controls, ports, and attributes. Here's an example:


.. code-block:: python

    class CounterNode(Node):
        category = 'demo'
    
        def build_node(self):
            self.text = self.add_text_control('0')
            self.button = self.add_button_control('Add')
    
        def init_node(self):
            self.i=0
            self.button.on_click += self.button_clicked
    
        def button_clicked(self):
            self.i += 1
            self.text.set(str(self.i))

With the code above, the number increases every time you press the "Add" button:

.. image:: https://i.imgur.com/RaWL7ez.png
   :width: 300px

Things you can do in ``init_node()``:

- initialize variables that will be used in the node
- add callbacks to controls or attributes

.. note::
    Do not confuse ``init_node()`` with ``build_node()``. See `Node Creation Process`_ for more details.




``restore_from_version()``
-------------------------

``restore_from_version()`` is called when a node is being upgraded (or downgraded) due to an extension being upgraded (or downgraded) for backward compatibility. When an extension is upgraded, Grapycal will delete all nodes of the old version and create new nodes of the new version. To make sure the user's data is not lost, Grapycal will call ``restore_from_version()`` to transfer the data from the old node to the new node.

Example usage:

.. code-block:: python

    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.restore_controls('control_a', 'control_b')
        self.restore_attributes('attr_a', 'attr_b')

Things you can do in ``restore_from_version()``:

- ``self.restore_controls()``: Transfer the state from the old controls to the new controls.
- ``self.restore_attributes()``: Transfer the value from the old attributes to the new attributes.

.. note::
    The ``version`` argument is intended to let the node switch between different restoring strategies based on the version of the old node. However, this feature is not implemented yet. Currently, the ``version`` argument is always ``''``.

.. note::
    Most restoration tasks can be done with ``restore_controls`` and ``restore_attributes``. For finer-grained control, use the data stored in ``old``. 

``destroy()``
-------------------------

``destroy()`` is called when a node is being deleted. Override this method to do cleanup tasks such as closing a file or releasing a resource. It's mandatory to return ``super().destroy()`` at the end of the method.

Example usage:

.. code-block:: python

    def destroy(self):
        self.file.close()
        return super().destroy()

----

We've seen the methods related to node creation and deletion. Next, let's see the "node event" methods. These methods are called when certain events happen to the node, so the node can interact with the graph or the user.

Things you can do in these methods:

- ``self.print()``: Print a message to the inspector panel.
- ``self.run()``: Run a complex custom task. There are 2 benefits to use ``self.run(task)`` instead of just ``task()``:

    *  If the task raises an exception, the exception will be caught and printed to the inspector panel instead of possibly crashing the whole program.
    *  The node event methods are possibly called from the UI thread. If the task takes a long time to run, the UI will freeze. ``self.run()`` will run the task in the execution thread to avoid freezing the UI.

For example:

.. code-block:: python
    
    class CnnNode(Node):
        ...
        
        def edge_activated(self, port: Port): # could be called from UI thread or execution thread
            self.run(self.task)

        def task(self): # will be called from execution thread no matter where edge_activated is called from
            x = self.in_port.get_one_data()
            y = self.cnn.forward(x) # this line may take a long time or raise an exception
            self.out_port.push_data(y)

``edge_activated()``
------------------------
Called when an edge on an input port is activated.

``input_edge_added()``
------------------------
Called when an edge is added to an input port.

``input_edge_removed()``
------------------------
Called when an edge is removed from an input port.

``output_edge_added()``
------------------------
Called when an edge is added to an output port.

``output_edge_removed()``
------------------------
Called when an edge is removed from an output port.

``double_click()``
------------------------
Called when the node is double clicked by an user.




.. _Node Creation Process:

Node Creation Process
========================

Here we clearify the node creation process in Grapycal.

``build_node()``, ``init_node()`` and ``restore_from_version()`` are the three methods related to node creation. In different cases, different methods will be called.

.. figure:: https://i.imgur.com/u0wGw9r.png
   :alt: Creation process of a node
   :align: center


   Creation process of a node

-   **The user creates a node from the node list**. In this case, ``build_node()`` then ``init_node()`` are called.

-   **The user deletes a node, then undo the deletion**. In this case, ``build_node()`` is not called, instead, Grapycal automatically restores the node's attributes,
    controls and ports. Then ``init_node()`` is called.

-   **A graph being load from disk**. Same as the second case.

-   **An extension being upgraded**. To upgrade an extension, Grapycal deletes the old node and creates a new one using the newly-defined node type.
    For the new node, ``build_node()``, ``restore_from_version()``, then ``init_node()`` are called.

Let's see an example. Suppose we have a node type called ``CounterNode`` with a text control and a button control.
When the user clicks the button, the text control will show the number of times the button is clicked.

.. code-block:: python

    class CounterNode(Node):
        category = 'demo'
    
        def build_node(self):
            self.text = self.add_control(TextControl, text='0')
            self.button = self.add_control(ButtonControl, label='Add')
    
        def init_node(self):
            self.i=0
            self.button.on_click += self.button_clicked
    
        def button_clicked(self):
            self.i += 1
            self.text.set(str(self.i))


Try pressing the button 3 times then delete the node and undo the deletion. The
controls are restored but ``i`` is not. So while the text control still shows ``3``, it will start from ``0``
again when you press the button.

To fix this, we need to save the count in an attribute. Attributes are saved and restored automatically.

.. code-block:: python

    class CounterNode(Node):
        category = 'demo'
    
        def build_node(self):
            self.text = self.add_control(TextControl, text='0')
            self.button = self.add_control(ButtonControl, label='Add')
            self.i = self.add_attribute('count', IntTopic, 0)
    
        def init_node(self):
            self.button.on_click += self.button_clicked
    
        def button_clicked(self):
            self.i.set(self.i.get() + 1)
            self.text.set(str(self.i.get()))

Now the count continues correctly after undoing the deletion.