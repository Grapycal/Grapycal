.. |ss| raw:: html

    <strike>

.. |se| raw:: html

    </strike>

Basic Usage
=============

In Grapycal's UI layout, the left-side-bar contains the node library and the settings button.
The rest of the window is the editor, where you can construct your graph.

.. figure:: https://i.imgur.com/gwDaxN0.png
    :align: center
    :width: 80%

    |ss| Yes, it's basically Scratch |se|

The node library contains all the nodes that are available to use. 
Drag them into the editor to create new instances of them.

Construct a Graph
-------------------

Let's create a simple graph that prints "Hello World!".

1. Drag an ``EvalNode`` and ``PrintNode`` into the editor and connect them together. 
2. Enter ``"Hello World!"`` into the ``EvalNode``'s text field.
3. Double click on the ``EvalNode`` to make it evaluate the expression. You should see "Hello World!" displayed in the ``PrintNode``.

.. figure:: https://i.imgur.com/6Cq3GbF.png
    :align: center
    :width: 80%

You can make the graph as complex as you want. Note that even the expression has been edited, an ``EvalNode`` will not evaluate it until being double clicked.

.. figure:: https://i.imgur.com/8wsG4WC.png
    :align: center
    :width: 80%

Undo/Redo
---------

You can undo/redo changes to the graph by pressing ``Ctrl+Z`` and ``Ctrl+Y`` respectively.