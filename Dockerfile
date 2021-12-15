FROM python:3.8-alpine

RUN apk add build-base

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /etc/supervisor/conf.d \
             /var/log/supervisor

COPY oalworkers.conf /etc/supervisor/conf.d/

COPY supervisord.conf /etc/

EXPOSE 8000

CMD [ "./entrypoint.sh" ]
