FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /Grapycal
COPY backend ./backend
COPY extensions ./extensions
RUN touch README.md
RUN pip install -e backend -e extensions/grapycal_builtin

CMD ["grapycal", "--host", "0.0.0.0", "--no-http"]

