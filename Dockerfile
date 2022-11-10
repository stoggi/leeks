FROM python:alpine as python

RUN pip install gunicorn flask ariadne apache-age-python psycopg2

COPY ./public ./public
COPY ./templates ./templates
COPY ./savoy.py .

EXPOSE 8080

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "savoy:app"]