FROM python:3.8-slim
WORKDIR /usr/src/app
COPY ./requirements.txt ./inaturalist-bot.py .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "./inaturalist-bot.py"]
