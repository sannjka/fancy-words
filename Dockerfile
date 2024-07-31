FROM python:3.9

ENV FLASK_CONFIG docker
WORKDIR /home/FancyWords


RUN apt-get update && apt-get install -y python3-pip python3-dev build-essential hdf5-tools libgl1 libgtk2.0-dev libhdf5-dev

COPY requirements requirements
RUN pip3 install --upgrade pip && pip install -r requirements/docker.txt

ENV PAINT_LOCAL 0
COPY migrations migrations
COPY app app
COPY run.py config.py boot.sh ./
RUN chmod 755 boot.sh

# runtime configuration
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
