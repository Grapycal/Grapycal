Nodes
===============

A node is a basic unit of a program. Each type of node performs a specific function, such as addition, getting or setting a variable, or reading a file.
Nodes can be connected together to form a graph that performs a more complex function.

A node consists of ports and controls. Ports serve as interfaces to other nodes, and controls serve as interfaces to the user.

List of built-in nodes
----------------------

Math
~~~~~~~~~~


.. |Addition| image:: https://i.imgur.com/yZoRJs3.png
    :height: 2em

|Addition| Addition 
++++++++++++++++++++++++++++++++++++++++++

Adds a set of values together.

- **Inputs**:
   -  **Values** - A set of values to add together. The values can be of any addable type, such as numbers, numpy arrays, or strings.

- **Outputs**:
    -  **Sum** - Sum of all values.

Subtraction
++++++++++++++++++++++++++++++++++++++++++

Calculates sum(`B`) - sum(`A`).

- **Inputs**:
   -  **A** - A set of values `A`
   -  **B** - A set of values `B`

- **Outputs**:
    -  **Difference** - sum(`B`) - sum(`A`)

Multiplication
++++++++++++++++++++++++++++++++++++++++++

Multiplies a set of values together.

- **Inputs**:
   -  **Values** - A set of values to multiply together. The values can be of any multipliable type, such as numbers or numpy arrays.

- **Outputs**:
    -  **Product** - Product of all values.

Division
++++++++++++++++++++++++++++++++++++++++++

Calculates product(`B`) / product(`A`).

- **Inputs**:
   -  **A** - A set of values `A`
   -  **B** - A set of values `B`

- **Outputs**:
    -  **Quotient** - product(`B`) / product(`A`)



