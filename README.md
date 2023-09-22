# Grapycal

![image](https://github.com/eri24816/Grapycal/assets/30017117/a67353e0-1818-4e5f-a670-6b21efda8cb5)

Grapycal is a visual scripting language based on Python.
It provides an graph editor for constructing programs
by adding nodes and linking them together.

Features:

- Interactive and dynamic: Easily track the active node while the program runs, insert real-time probes to inspect data, and modify the running graph on-the-fly for instant changes in its behavior.

- Extendable: Grapycal allows users to create custom nodes for any domains, such as deep learning, robotics, or music synthesis. The node extensions can be shared as python packages.

-  Collaborative



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
