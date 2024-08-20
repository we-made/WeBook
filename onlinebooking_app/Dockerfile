
FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install gunicorn

COPY . .

CMD [ "gunicorn", "-w", "4", "app:app", "-b", "0.0.0.0:5100" ]