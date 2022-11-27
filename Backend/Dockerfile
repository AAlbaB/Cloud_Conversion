# Pull Image
FROM python:3.9-slim-buster

# Install and update dependencies
RUN apt-get -y update
RUN apt-get install -y ffmpeg

# Set Work Directory
WORKDIR /tareas

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Expose port 8080
EXPOSE 8080

# Install dependencies and requirements
RUN pip install --upgrade pip
COPY ./requirements.txt /tareas/requirements.txt
RUN pip install -r requirements.txt

COPY . /tareas/

# Entrypoint for tareas
ENTRYPOINT ["gunicorn","--bind","0.0.0.0:8080","tareas:app"]