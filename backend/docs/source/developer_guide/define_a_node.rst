Define a Node Type
======================

To define a node type, you need to create a class that extends the ``FunctionNode``, ``SourceNode``, or ``Node`` class.
If the node behaves like a function, extend ``FunctionNode``. If the node behaves like a source of data, extend ``SourceNode``. ``FunctionNode`` and  ``SourceNode`` are both subclasses of ``Node``, providing higher-level interfaces that make it easier to define nodes.

If they do not fit your needs, you can extend the ``Node`` class directly.

See:

.. toctree::
    :titlesonly:

    define_a_node_from_higher_level
    define_a_node_from_node