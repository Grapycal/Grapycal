Application Structure
=============================

The Grapycal application consists of the server (written in Python) and the client (written in Typescript). The server is responsible for managing all logics and state. The client can be seen as just a view of the server state, while user can also modify the state from the client. 

To implement automatic state syncronization, we wrap two layers of abstractions on top of websocket: `Topics` and `SObjects`.

A topic is a piece of data that is shared across the server and the client. When either side changes a topic, the change is automatically broadcasted to the other side with websocket, and the other side will update the topic accordingly and reflect to the change if necessary. Thus, with a set of topics, we can easily share all the state in the application.

`SObjects`

.. image:: https://i.imgur.com/8fWPdNC.png
    :height: 250px
    :align: center