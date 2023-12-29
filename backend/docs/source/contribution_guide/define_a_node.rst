Extension
======================

All nodes in Grapycal are defined in extensions. An extension is a Python module/package that meets the following requirements:

- Its name must start with ``grapycal_``.

If an extension is installable, it sould list ``grapycal`` in the dependencies. It's recommanded to use ``>=`` or ``0.*`` as the version constraint because Grapycal is still in ``0.x`` and the minor version may be bumped frequently. We'll try to keep the API backward compatible.

A Grapycal extension contains multiple node type definitions, which look like this:

.. code-block:: python

    # grapycal_builtin/__init__.py

    class Node1(Node):
        ...

    class Node2(Node):
        ...

To define a node type, you need to create a class that extends the ``FunctionNode``, ``SourceNode``, or ``Node`` class.
``FunctionNode`` and  ``SourceNode`` are both subclasses of ``Node``, providing higher-level interfaces to define nodes.

The source code of `grapycal_builtin <https://github.com/Grapycal/Grapycal/tree/dev/grapycal_builtin/grapycal_builtin>`_ contains various concrete examples of node definitions, which would be helpful for understanding how to define a node.

See:

.. toctree::
    :titlesonly:

    define_a_node_from_higher_level
    define_a_node_from_node

Usage of an extension
----------------------

When a Grapycal workspace runs, it goes through the module search path to discover locally available extensions. (In other words, to be discoverd by Grapycal, an extension can either be installed or just be placed in the current working directory.) Once they're discoverd, they can be imported into a workspace via the UI. After imported, the nodes defined in the extensions will be available in the workspace. Besides, Grapycal also provides `a list of recommended extensions <https://github.com/Grapycal/grapycal_data/raw/main/data.yaml>`_ on PyPI, which can be directly installed (then imported) via the UI.
