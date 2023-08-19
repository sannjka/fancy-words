FROM python:3.9-alpine

ENV FLASK_CONFIG docker
WORKDIR /home/FancyWords

COPY requirements requirements
RUN pip install --upgrade pip && pip install -r requirements/docker.txt

COPY migrations migrations
COPY app app
COPY run.py config.py boot.sh ./
RUN chmod 755 boot.sh

# runtimee configuration
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
