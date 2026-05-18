FROM python:3.12-slim
WORKDIR /app
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/dev.txt
COPY . .
EXPOSE 8000
CMD [ "gunicorn","config.wsgi:application","--bind","0.0.0.0:8000" ]

