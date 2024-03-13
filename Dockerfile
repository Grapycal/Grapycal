FROM python:3.11-alpine3.19

RUN pip install grapycal grapycal-builtin

WORKDIR /grapycal

ENTRYPOINT ["grapycal", "--host", "0.0.0.0", "grapycal"]