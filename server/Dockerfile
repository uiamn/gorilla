FROM python:3.10-slim

RUN python -m pip install flask flask_cors requests gunicorn

# initialize
ADD . /server

WORKDIR /server
RUN python initialize.py

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "gunicorn", "--workers", "3", "--bind", "0.0.0.0:80", "server:app"]
