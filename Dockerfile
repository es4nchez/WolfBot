FROM python:3.11-slim-bookworm

WORKDIR /bot

RUN mkdir -p databases

ADD . /bot

RUN pip install --no-cache-dir -r requirements.txt


CMD ["python3", "WolfBot.py"]