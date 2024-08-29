# Use an official Python runtime as a parent image
FROM python:3.12-slim

# remove the "/app" to not have to remove the "app." in the imports -> maybe only remove it in docker-compose for local
WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080" ]