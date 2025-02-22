# Cloud Coder Bot

This is a Telegram bot built with `aiogram` that provides expert solutions for cloud-related queries, including AWS deployment, Kubernetes setup, CI/CD configuration, and serverless architectures.

## Features
- Handles inline button selections for predefined cloud solutions.
- Processes user queries and provides expert responses.
- Supports chunked message responses to avoid Telegram's character limit.

## Installation

### Prerequisites
Ensure you have the following installed:
- Python 3.10+
- `pip` package manager
- Telegram Bot Token (from BotFather)

### Clone the Repository
```sh
$ git clone https://github.com/your-repo/cloud-coder-bot.git
$ cd cloud-coder-bot
```

### Install Dependencies
```sh
$ pip install -r requirements.txt
```

## Configuration

### AI Model Configuration
The bot uses [zephyr-7b-beta](https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta) for AI inference.

### Set Up Environment Variables
Create a `.env` file in the project root and add:
```ini
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
API_URL=model_api_url
HF_API_TOKEN=hugging_face_api_key
```

## Running the Bot
```sh
$ python3 bot/main.py
```

## Troubleshooting and Issues Faced


### "Bad Request: can't parse entities"
If markdown formatting issues arise, ensure special characters are properly escaped in responses.
Use parse_mode="MarkdownV2" or parse_mode="HTML" carefully.
Test responses with smaller message chunks.

### "Bot Not Responding"
Cause: Invalid token, API connectivity issues, or unhandled exceptions.
Solution:
Verify that TELEGRAM_BOT_TOKEN is set correctly in .env.
Review logs for errors and exceptions.

### "Rate Limits Exceeded"
Cause: Excessive requests to Telegram API.
Solution:
Implement exponential backoff on API calls.
Ensure messages are spaced out and avoid flooding the chat.


## Lessons Learned

### Efficient Message Handling: 
Chunking responses prevents exceeding Telegram's message size limit.

### Error Handling, Logging and Instrumentation: 
Implementing robust exception handling reduces unexpected crashes and improves debugging ensures quick issue resolution.

### API Rate Limiting: 
Managing request frequency helps avoid being blocked by Telegram.

### Security Best Practices: 
Storing API tokens securely using .env files prevents leaks.


## Contributing
Feel free to fork this project and submit pull requests.

