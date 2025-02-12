FROM python:3.10-slim-bullseye

WORKDIR /app
COPY requirements/base.txt ./requirements/base.txt
COPY requirements/local.txt ./requirements/local.txt
COPY requirements/production.txt ./requirements/production.txt

ENV DJANGO_DEBUG=True
#ENV DJANGO_SECRET_KEY='THISISMYSECRETKEYTOSEIFITALLWORKS'
ENV DJANGO_ALLOWED_HOSTS='*'
ENV ALLOWED_HOSTS='*'
ENV DJANGO_SETTINGS_MODULE='config.settings.local'


RUN apt update && apt install -y curl
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt install -y nodejs python3-dev libpq-dev gcc
RUN pip install --no-cache-dir -r requirements/local.txt
RUN pip install --no-cache-dir -r requirements/production.txt
RUN pip install gunicorn
RUN pup install numpy
RUN pip install pandas

COPY . .

RUN rm -rf node_modules && rm -f package-lock.json && npm i

RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "--preload", "-b", "0.0.0.0:8080", "config.wsgi:application", "--threads", "6", "-w", "6"]


