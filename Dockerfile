FROM python:3.10-slim

WORKDIR /app

COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

EXPOSE 8000

# Run the bot
CMD ["python3", "-m", "bot.main"]
