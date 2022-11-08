FROM python:3.10-alpine
WORKDIR /app

ENV FLASK_APP host.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 8883

COPY ./app /app

RUN apk add --no-cache gcc musl-dev linux-headers openssl-dev libffi-dev
RUN pip install -r requirements.txt

CMD ["flask", "run", "--no-reload"]