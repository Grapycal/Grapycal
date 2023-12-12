FROM python:3.11

WORKDIR /Grapycal

RUN pip install grapycal grapycal-builtin

EXPOSE 8765 9001
CMD ["python", "-m", "grapycal", "--host", "0.0.0.0"]