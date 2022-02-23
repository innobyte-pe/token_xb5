# base image
FROM python:3.8.5-alpine

# instalando dependencias
RUN apk update && \
    apk add --virtual build-deps gcc python3-dev musl-dev && \
    apk add mysql-dev && \
    apk add netcat-openbsd && \
    apk add mysql-client && \
    apk add g++


# estableciendo directorio de trabajo
WORKDIR /usr/src/app

# agregando e instalando requirements
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# agregando app
COPY . /usr/src/app

# agregando entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# ejecutar server
CMD ["/usr/src/app/entrypoint.sh"]