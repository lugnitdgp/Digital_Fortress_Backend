FROM python:3.7-slim-buster

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# WORKDIR /app

ENTRYPOINT [ "sh", "entrypoint.sh" ]