FROM python:3.9.12-slim

ADD app /app/
# Creates the log folder instance that can be mapped with a mountpoint
# when running docker run or docker-compose
RUN mkdir /log

WORKDIR /app
RUN ["pip", "install", "-r", "requirements.txt"]
CMD ["python", "main.py"]
