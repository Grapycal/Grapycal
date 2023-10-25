Application Structure
=============================


The Grapycal application consists of the server (written in Python) and the client (written in Typescript). The server manages all logics and state. The client is just a view of the server state, while user can also modify the state from the client. 

To elegantly implement state syncronization between the server and the client, we wrap two layers of abstractions on top of websocket: `Topics` and `SObjects`.

A `topic` is **a piece of data** that is shared across the server and the client. When either side changes a topic, the change is automatically broadcasted to the other side with websocket so the other side can update the topic accordingly and reflect to the change if necessary.

A `SObject` is **an object** that is shared across the server and the client. Each `SObject` owns a specific set of `attributes`, implemented with `topics`, syncronized between the server and the client.

.. figure:: https://i.imgur.com/8fWPdNC.png
    :height: 250px
    :align: center

    The concept of SObject and topic. `o1` and `o2` are SObjects. `t1` - `t5` are topics. `t1` and `t2` are attributes of `o1`. `t3`, `t4` and `t5` are attributes of `o2`.

Many class in Grapycal inherits from SObject, such as `Node`, `Edge`, `Port`, etc.. In a workspace, they are organized in a tree structure:

.. code-block:: text

    root
    └───Workspace
        ├───Sidebar
        │   ├───AdditionNode
        │   │   └──...     
        │   ├───EvalNode
        │   │   └──... 
        │   └───PrintNode
        │   │   └──... 
        └───Editor
            ├───AdditionNode
            │   └──... 
            ├───EvalNode
            │   └──... 
            ├───PrintNode
            │   └──... 
            ├───EvalNode
            │   └──... 
            ├───Edge
            └───Edge

The `Sidebar` contains preview of all the nodes that can be added to the editor. The `Editor` contains all the nodes and edges been added to it.

In each node, there are `ports` and `controls`. For example:

.. code-block:: text

    SomeTypeOfNode
    ├───Port
    ├───Port
    ├───TextControl
    └───ButtonControl


