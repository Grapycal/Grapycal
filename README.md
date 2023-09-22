# Grapycal

![image](https://github.com/eri24816/Grapycal/assets/30017117/a67353e0-1818-4e5f-a670-6b21efda8cb5)

Grapycal is a visual scripting language based on Python.
It provides an graph editor for constructing programs
by adding nodes and linking them together.

Grapycal is a visual scripting language based on Python. It provides a web-based editor for constructing programs by adding nodes and linking them together into a graph.

Features:

- Interactive: On the GUI, users can run different parts of the graph in arbitrary order, inspect variables in real-time with data visualizers, and easily track the active node while the program runs.

- Dynamic: Grapycal runs a graph in real-time without compiling, allowing users to modify the running graph for instant changes in its behavior. That includes adjusting node parameters, adding or removing nodes from a workflow, and terminating a loop at any time.

- Extendable: Grapycal provides a Python API allowing users to create custom nodes for any domain, such as deep learning, robotics, or music synthesis. Node developers can add UI controls including ports, input boxes, images, and buttons to a node with few lines of code.

- Collaborative: Custom node definitions can be shared as Python packages for others to use. Thus, nodes for various domains can be mixed in a graph to form a powerful tool or a creative artwork (I’ll create some examples when I have time). What’s more, Grapycal can interact with multiple clients simultaneously, allowing a group of people to work on the same graph over the Internet.

Grapycal is not (yet):

- Fast: Grapycal is yet another layer of abstraction on top of Python. Some overhead is introduced for its interactivity and dynamics. However, the overhead would be relatively small if the graph doesn’t run at a high frequency ( less than ~1000 node runs per second ). For example, if your program mainly computes with C extensions (such as NumPy) or uses GPU heavily (such as deep learning tasks), you shouldn’t feel an impact on performance.

- Stable: Grapycal is not heavily tested to ensure the graph always runs as expected.

## Motivation

The strength of Grapycal lies not in writing stable and well-defined programs, but in conducting experiments, including training AI, physical simulations, data analysis, computer art, and more. These experiments require repeated parameter adjustments, swapping certain components of models, while simultaneously observing the phenomena generated by different parameters. We then use human judgment combined with domain knowledge to deduce the best model or certain other conclusions.

In this back-and-forth process between human and machine, using traditional Python execution methods or Jupyter notebooks can be quite sluggish. Therefore, we need the higher interactivity provided by Grapycal.

## Documentation

The full documentaition can be found [here](https://eri24816.github.io/Grapycal/).

## Installation (for Development)

backend:

```
cd backend
pip install -e .
```

or

```
cd backend
poetry install
```

frontend:

```
cd frontend
npm install
```

## Dependencies

Grapycal and its dependences consist of the following 6 packages:

- [Grapycal/backend](https://github.com/eri24816/Grapycal): Included in this repo, including the backend code of the Grapycal main application

- [Grapycal/frontend](https://github.com/eri24816/Grapycal): Included in this repo, including the frontend code of the Grapycal main application


- [Chatroom](https://github.com/eri24816/ChatRoom) and [ObjectSync](https://github.com/eri24816/ObjectSync): Backend dependencies. Python packages.

- [ChatroomClient_ts](https://github.com/eri24816/ChatRoomClient_ts) and [ObjectSyncClient_ts](https://github.com/eri24816/ObjectSyncClient_ts): Frontend dependencies. npm packages.

## Run App (for Development)

1. run Grapycal server
```
cd backend
scripts/run.sh
```

2. run web server
```
cd frontend
npm run app
```

3. Go to `localhost:9001` with a web browser.
