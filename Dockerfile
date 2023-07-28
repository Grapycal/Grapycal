FROM python:3.11

# install node

RUN apt-get update && apt-get install -y nodejs npm

WORKDIR /Grapycal

COPY . .

# install python dependencies in ./backend

RUN pip install -e ./backend

# install node dependencies in ./frontend

RUN rm frontend/package-lock.json && npm install --prefix ./frontend

EXPOSE 8765 9001

CMD ["sh", "docker_cmd.sh"]