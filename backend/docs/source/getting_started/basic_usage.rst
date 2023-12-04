.. |ss| raw:: html

    <strike>

.. |se| raw:: html

    </strike>

Basic Usage
=============

In Grapycal's UI layout, there are 3 main parts: the function tabs (node list by default), the graph editor and the inspector.

.. figure:: https://i.imgur.com/5iC9bIs.png
    :align: center
    :width: 100%


The node list contains all the nodes to use. To create a node, you can either:

1. drag them into the editor.
2. type the nodes' names directly and select the one you want from the auto-complete list.

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

Operations and Hotkeys 
--------

* ``wheel on editor``: Zoom in/out.
* ``drag on editor``: Pan.
* ``Ctrl + S``: Save the workspace.
* ``Ctrl + Z``: Undo.
* ``Ctrl + Y``: Redo.
* ``Ctrl + Q``: Quit the application.
* ``Shift + click node or edge``: Select multiple nodes or edges (additive).
* ``Ctrl + click node or edge``: Select multiple nodes or edges (toggle).
* ``Ctrl + drag editor``: Rectangular select.
* ``Alt + drag node``: Disables the auto-layout and allows you to move the node freely.
* ``Tab``: Toggle the inspector.

Function Tabs
--------------

Function tabs are located on the left side of the window. They are used to manage the workspace.

File 📁
^^^^

The file tab lists all the files in the current working directory (cwd). You can open a Grapcal workspace file (\*.grapycal) by double clicking on it.

Node List 📜
^^^^

The node list tab contains all the nodes that can be used in the graph. You can view them, pick one you like and drag it into the editor.

Extensions 🚀
^^^^

The extensions tab comprises with three sections, In Use, Available and Not Installed.

* In Use: Lists all the extensions that are imported in the current workspace.
* Available: Lists all the extensions that are installed but not imported in the current workspace.
* Not Installed: Provides some recommended extensions on PyPI. You can install them by clicking the install button.

Settings 🛠️
^^^^

The settings tab allows you to change the settings of the current workspace or preferences.

Examples💡
^^^^

This tab has not been implemented yet. It will contain some example files that can be downloaded and opened.

About
^^^^

About is about.

Inspector
------------

The inspector is used to view and edit the attributes of the selected nodes. It is located on the right side of the window.

