FROM python:3.7

ARG PORT
ARG HOST
ARG DB
ARG DEBUG
ENV PORT $PORT
ENV DB_HOST $HOST
ENV DB_NAME $DB
ENV DEBUG $DEBUG
RUN apt-get update
RUN apt-get install -y python python-pip python-dev
RUN pip install pipenv
ADD . /app
WORKDIR /app
RUN pipenv install --system --deploy --ignore-pipfile
EXPOSE $PORT

CMD python main.py
