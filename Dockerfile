FROM python:3.10-alpine

RUN pip install --no-cache-dir gunicorn dash pandas

COPY /src/ /src/

WORKDIR /src

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:server"]
