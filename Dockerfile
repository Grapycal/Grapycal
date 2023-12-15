FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /Grapycal

RUN pip install grapycal grapycal-builtin

EXPOSE 8765
CMD ["python", "-m", "grapycal", "--host", "0.0.0.0", "--no-serve-webpage"]