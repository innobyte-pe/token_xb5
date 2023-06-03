FROM python:3.8.5

# nuevo
# instalando dependencias
RUN apt-get update && \
    apt-get install -y gcc python3-dev libffi-dev libssl-dev && \
    apt-get install -y default-libmysqlclient-dev netcat-openbsd g++


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