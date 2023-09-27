Define a Node Type: The Easy Way
==================================================================

This is guide about defining a node type from the ``FunctionNode`` or ``SourceNode`` Class

FunctionNode
------------

.. code-block:: python

    class AdditionNode(FunctionNode):
        '''
        Adds a set of numbers together.
        '''
        category = 'function/math'
        inputs = ['numbers']
        input_edge_limit = [None]
        outputs = ['sum']

        def calculate(self, data: List[List[Any]]):
            # Retrive data from the first port (the only port)
            data = data[0]

            # Return the sum of all the numbers coming in from the port
            return sum(data)

.. image:: https://i.imgur.com/sAq1jNW.png
    :align: center