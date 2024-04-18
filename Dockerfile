FROM python:3.12

ENV PYTHONBUFFERED 1

WORKDIR /src

COPY . /src/

RUN pip install -r requirements.txt

EXPOSE 8000

RUN chmod +x docker-entrypoint.sh

ENTRYPOINT [ "./docker-entrypoint.sh" ]