
grapycal.builtin_nodes
==================

Interaction
------------------

Print
~~~~~~~~~~~~~~~~~~~
Display the data received from the input edge.

:Inputs:
    - **data**: data to be displayed



Eval
~~~~~~~~~~~~~~~~~~~
Equivalent to Python's `eval` function. It evaluates the expression in the input text box and send out the result.

To make it run, either send in a signal to the `run` input port, or double click on the node.

:Inputs:
    - **run**: send in a signal to evaluate the expression

:Outputs:
    - **result**: the result of the expression



Exec
~~~~~~~~~~~~~~~~~~~
Equivalent to Python's `exec` function. It executes the statements in the input text box.

To make it run, either send in a signal to the `run` input port, or double click on the node.

:Inputs:
    - **run**: send in a signal to run the statements
    

:Outputs:
    - **done**: send out a signal when the statements are done


Data
------------------

Variable
~~~~~~~~~~~~~~~~~~~
VariableNode stores a variable in the workspace. It can be used to store data for later use.

:Inputs:
    - **run**: send in a signal to actively output the variable's value
    - **set**: set the variable's value

:Outputs:
    - **get**: get the variable's value



Split
~~~~~~~~~~~~~~~~~~~
SplitNode is used to get items from a list or a dictionary using keys.
It is equivalent to `data[key]` in Python.

Multiple keys can be used at the same time. Each value will be sent to a corresponding output port.

:Inputs:
    - list/dict: the list or dictionary to be split

:Outputs:
    - **value1**: the value of the first key
    - **value2**: the value of the second key
    etc.


Function/math
------------------

Addition
~~~~~~~~~~~~~~~~~~~
Adds a set of values together. The values can be of any addable type, such as numbers, NumPy arrays,
PyTorch tensors, or strings.

:Inputs:
    - **values**: a set of values
    
:Outputs:
    - **sum**: sum of all values


Subtraction
~~~~~~~~~~~~~~~~~~~
Calculates sum(`B`) - sum(`A`).

:Inputs:
   - **A**: A set of values, `A`
   - **B**: A set of values, `B`

:Outputs:
    - **Difference**: sum(`B`) - sum(`A`)


Multiplication
~~~~~~~~~~~~~~~~~~~
Multiplies a set of values together. The values can be of any multipliable type, such as numbers, NumPy arrays, or
PyTorch tensors.

:Inputs:
    - **values**: a set of values

:Outputs:
    - **product**: product of all values


Division
~~~~~~~~~~~~~~~~~~~
Calculates product(`B`) / product(`A`).

:Inputs:
    - **A**: A set of values, `A`
    - **B**: A set of values, `B`

:Outputs:
    - **Quotient**: product(`B`) / product(`A`)


Function
------------------

Lambda
~~~~~~~~~~~~~~~~~~~
LambdaNode is one of the most powerful nodes in Grapycal. It allows you to define any function
similar to Python's lambda function.

It can be freely configured to be any function of any number of inputs and outputs.

:Inputs:
    - **x**: input 1
    


Procedural
------------------

For
~~~~~~~~~~~~~~~~~~~

Event
~~~~~~~~~~~~~~~~~~~

Procedure
~~~~~~~~~~~~~~~~~~~

Limiter
~~~~~~~~~~~~~~~~~~~
