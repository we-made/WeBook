FROM python:3.8-slim

ENV APP_HOME /app
WORKDIR $APP_HOME

# ENV setup
ENV DJANGO_DEBUG=True
ENV DJANGO_ALLOWED_HOSTS='*'
ENV ALLOWED_HOSTS='*'
ENV DJANGO_SETTINGS_MODULE='config.settings.local'

# Removes output stream buffering, allowing for more efficient logging
ENV PYTHONUNBUFFERED 1

# OS level Dependencies
RUN apt update && apt install -y curl
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
RUN apt install -y nodejs python3-dev libpq-dev gcc

# Install dependencies
COPY requirements/base.txt ./requirements/base.txt
COPY requirements/local.txt ./requirements/local.txt
COPY requirements/production.txt ./requirements/production.txt
RUN pip install --no-cache-dir -r requirements/local.txt
RUN pip install --no-cache-dir -r requirements/production.txt

# Copy code to container
COPY . .

CMD python scheduler.py