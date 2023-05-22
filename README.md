# Grapycal

## Installation (for Development)

The installation process is a bit complicated because Grapycal involves the following 6 packages:

- [Grapycal/backend](https://github.com/eri24816/Grapycal): Included in this repo, including the backend code of the Grapycal main application

- [Grapycal/frontend](https://github.com/eri24816/Grapycal): Included in this repo, including the frontend code of the Grapycal main application


- [Chatroom](https://github.com/eri24816/ChatRoom) and [ObjectSync](https://github.com/eri24816/ObjectSync): Backend dependencies. Python packages.

- [ChatroomClient_ts](https://github.com/eri24816/ChatRoomClient_ts) and [ObjectSyncClient_ts](https://github.com/eri24816/ObjectSyncClient_ts): Frontend dependencies. npm packages.

The latter 4 packages is not yet uploaded the PYPI or the npm registry (I'll try to do that soon). You have to manually download their source code and install with `pip install -e` for the two python (backend) packages and `npm install` for the two npm (fontend) packages.

While installing the npm packages, please use `npm link` and `npm link <package name>` to manually link `ChatroomClient_ts` to `ObjectSyncClient_ts`, and `ObjectSyncClient_ts` to `Grapycal`.

## Run App (for Development)

1. run Grapycal server
```
cd backend
python scripts\main.py
```

2. run web server
```
cd frontend
npm run app
```

3. Go to `localhost:9001` with a web server.