Define a Node Type
======================

To define a node type, you need to create a class that extends the ``FunctionNode``, ``SourceNode``, or ``Node`` class.
``FunctionNode`` and  ``SourceNode`` are both subclasses of ``Node``, providing higher-level interfaces to define nodes.

The source code of `grapycal-builtin <https://github.com/eri24816/Grapycal/tree/dev/grapycal_builtin/grapycal_builtin>`_ contains various concrete examples of node definitions, which would be helpful for understanding how to define a node.

See:

.. toctree::
    :titlesonly:

    define_a_node_from_higher_level
    define_a_node_from_node