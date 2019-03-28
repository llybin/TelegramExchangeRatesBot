FROM python:3.7.2-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY wait-for-it.sh ./

RUN pip install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --dev

COPY . .

CMD [ "python manage.py start" ]
