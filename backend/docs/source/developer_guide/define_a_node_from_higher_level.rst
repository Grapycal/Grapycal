Define a Node Type: The Easy Way
==================================================================

This is a guide about defining a node type from the ``FunctionNode`` or ``SourceNode`` Class

FunctionNode
------------

The ``FunctionNode`` class is a node that takes in data from one or more ports, performs a calculation on the data, and outputs the result to one or more ports. It is passive i.e. it only activates when there is data on all of its input ports.

To define a ``FunctionNode``, simply define the following:

-  ``category``: The category of the node. This is used to group nodes together in the node library.
-  ``inputs``: A list of the names of the input ports.
-  ``outputs``: A list of the names of the output ports.
-  ``calculate()``: A function that takes the input data and returns the output data.
    * Arguments: For each input port, one argument will be passed to the function. Each argument will be a list of data from all edges connected to that port. 
    * Return: A dictionary of the output data to send to every output port. The keys of the dictionary should be the names of the output ports. For each output port, all its edges will receive the same data. If there is only one output port, then the dictionary is omitted and the data should be returned directly.

-   ``max_in_degree`` (Optional): A list of the maximum number of edges that can be connected to each input port. If ``None`` is specified, then there is no limit.
-   ``display_port_names`` (Optional): A boolean that determines whether the port names are displayed on the node. Defaults to ``True``.
-   Since ``FunctionNode`` is a subclass of ``Node``, you can also do everything in :doc:`define_a_node_from_node` to further customize the node.

.. code-block:: python

    class AdditionNode(FunctionNode):
        '''
        Adds a set of numbers together.
        '''
        category = 'function/math'
        inputs = ['numbers']
        max_in_degree = [None]
        outputs = ['sum']

        def calculate(self, numbers:List[Any]):
            return sum(data)

.. image:: https://i.imgur.com/sAq1jNW.png
    :align: center

SourceNode
-----------------

Unlike the passive ``FunctionNode``, the ``SourceNode`` class actively sends data to its output ports when dobule-clicked or receives a signal from from its run port. It is usually used to start a graph running.

To define a ``SourceNode``, simply define the following:

-  ``task()``: The task to perform when the node runs. Usually pushs data to its output ports.

-  Since ``SourceNode`` is a subclass of ``Node``, you can also do everything in :doc:`define_a_node_from_node` to further customize the node.
