FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    gcc \
    libkrb5-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --no-cache-dir -r requirements.txt


COPY . .


CMD ["python3", "-m", "bot.main"]
