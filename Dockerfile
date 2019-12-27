FROM python:3.8.1-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY wait-for-it.sh ./

RUN pip install --upgrade pip

RUN pip install pipenv==2018.11.26

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --dev --deploy

COPY . .

CMD ["python manage.py start"]
