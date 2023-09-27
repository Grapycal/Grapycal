Define a Node Type: The Easy Way
==================================================================

This is a guide about defining a node type from the ``FunctionNode`` or ``SourceNode`` Class

FunctionNode
------------

The ``FunctionNode`` class is a node that takes in data from one or more ports, performs a calculation on the data, and outputs the result to one or more ports.

To define a ``FunctionNode`` you must define the following:

-   ``category``: The category of the node. This is used to group nodes together in the node library.
-   ``inputs``: A list of the names of the input ports.
-   ``max_in_degree``: A list of the maximum number of edges that can be connected to each input port. If ``None`` is specified, then there is no limit.
-   ``outputs``: A list of the names of the output ports.
-  ``calculate()``: A function that takes the input data and returns the output data.
    * Argument ``data``: A list of lists of data. Each list of data corresponds to the data coming in from each input port. The length of the list is equal to the number of input ports.
    * Return: If there is only one output port, then one data entry should be returned. It will be sent to all edge of the output port. If there are multiple output ports, then a list of data should be returned. Each data entry will be sent to all edges of each output port.

.. code-block:: python

    class AdditionNode(FunctionNode):
        '''
        Adds a set of numbers together.
        '''
        category = 'function/math'
        inputs = ['numbers']
        max_in_degree = [None]
        outputs = ['sum']

        def calculate(self, data: List[List[Any]]):
            # Retrive data from the first port (the only port)
            data = data[0]

            # Return the sum of all the numbers coming in from the port
            return sum(data)

.. image:: https://i.imgur.com/sAq1jNW.png
    :align: center