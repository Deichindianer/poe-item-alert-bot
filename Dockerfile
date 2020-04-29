FROM python:3.8.2

COPY requirements.txt requirements.txt

# Install all the deps
RUN pip install -r requirements.txt

COPY poe-item-alert-bot .

CMD ["python", "bot.py"]


