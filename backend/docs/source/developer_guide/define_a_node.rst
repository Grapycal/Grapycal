Define a Node Type
======================

This guide provides a comprehensive explanation of how to define a node type in Grapycal.

A node type in Grapycal must inherit from the grapycal.Node class and can implement various methods to define its behavior. This guide will walk you through the key methods involved in defining a node type.

Specify the Category
-------------------------

The category is used to group nodes in the node list. For example:

.. code-block:: python

    class CounterNode(Node):
        category = 'demo'

``build_node()``
-------------------------
The ``build_node()`` method is called once when a node is created. This is where you define the structure of the node, including      :doc:`controls`,
:doc:`port`,
and :doc:`attribute`.
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
``restore_from_version()`` is called when a node is being upgraded (or downgraded) due to an extension being upgraded (or downgraded).
Maintaining backward compatibility is a key feature of Grapycal. When an extension is upgraded, Grapycal will delete all nodes of the old version and create new nodes of the new version. To make sure the user's data is not lost, Grapycal will call ``restore_from_version()`` to transfer the data from the old node to the new node.

Example usage:

.. code-block:: python
    def restore_from_version(self, version: str, old: NodeInfo):
        super().restore_from_version(version, old)
        self.recover_controls('some_control', 'some_other_control')
        self.recover_attributes('some_attribute', 'some_other_attribute')





.. _Node Creation Process:

Node Creation Process
-------------------------



``build_node()``, ``init_node()`` and ``restore_from_version()`` are the three methods related to node creation.

In different cases, different methods will be called.

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