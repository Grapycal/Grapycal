Developer Guide: Overview
=========================

Grapycal is still in its early stage. Any contribution is welcome. Currently, most of our efforts are on the backend (the core of Grapycal) and extensions (nodes with various functionalities), but it's also helpful to improve the frontend and the documentation.

To discuss, feel free to open an issue or join the `Discord server <https://discord.gg/adNQcS42CT>`_.

Application Structure
----------------------------


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

In each node, there can be `ports` and `controls`. For example:

.. code-block:: text

    SomeTypeOfNode
    ├───Port
    ├───Port
    ├───TextControl
    └───ButtonControl

A `port` is a connection point for edges. A `control` is a UI element that allows user to interact with the node. `Ports` and `controls` can be added to a node in the building process of the node, or be added (or removed) dynamically as the node's runtime behavior. For example, the lambda node creates a port each time user adds a new input variable.



