FROM python:alpine as python

RUN pip install gunicorn flask ariadne neo4j authlib requests

COPY ./public ./public
COPY ./templates ./templates
COPY ./leeks ./leeks
COPY ./main.py .

EXPOSE 8080

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "main:app"]