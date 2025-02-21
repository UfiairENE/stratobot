import asyncio
from aiogram import Router, types, F
from bot.utils.inference import get_cloud_solution  
from loguru import logger
from aiogram.utils.text_decorations import markdown_decoration

router = Router()

GREETINGS = {'hello', 'hi', 'hey', 'greetings', 'hola', 'sup', 'yo'}

@router.callback_query(F.data.in_(["aws_deploy", "k8s_setup", "cicd", "serverless"]))
async def cloud_task_handler(callback_query: types.CallbackQuery):
    """Handles inline button selections for predefined cloud solutions."""
    cloud_prompts = {
        "aws_deploy": {
            "query": "How to deploy a Python app on AWS?",
            "context": "Production-ready AWS deployment with monitoring and scaling"
        },
        "k8s_setup": {
            "query": "How to set up a Kubernetes cluster?",
            "context": "Production Kubernetes cluster with security and monitoring"
        },
        "cicd": {
            "query": "How to configure a CI/CD pipeline?",
            "context": "Enterprise-grade CI/CD pipeline with testing and security"
        },
        "serverless": {
            "query": "How to deploy a serverless function?",
            "context": "Production serverless architecture with monitoring"
        }
    }

    task = callback_query.data
    if task in cloud_prompts:
        await callback_query.answer()  

        task_info = cloud_prompts[task]
        enhanced_query = f"{task_info['query']} Provide a production-ready solution with {task_info['context']}"

        try:
            response = await get_cloud_solution(enhanced_query)  
            await send_chunked_response(callback_query.message, response)
            logger.info(f"User {callback_query.from_user.id} received expert response for {task}")
        except Exception as e:
            logger.error(f"Error processing cloud task: {e}")
            await callback_query.message.answer("Sorry, an error occurred while processing your request.")

def escape_markdown_v2(text: str) -> str:
    """
    Escapes special characters for Telegram's MarkdownV2 format.
    """
    chars_to_escape = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in chars_to_escape:
        text = text.replace(char, f'\\{char}')
    return text

async def send_chunked_response(message: types.Message, response: str, chunk_size=4000):
    """
    Splits long responses into chunks and sends them sequentially.
    Handles markdown formatting safely with fallback to plain text.
    """
    chunks = []
    current_chunk = ""
    
    # Split by newlines to preserve formatting blocks
    lines = response.split('\n')
    
    for line in lines:
        if len(current_chunk) + len(line) + 1 <= chunk_size:
            current_chunk += line + '\n'
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = line + '\n'
    
    if current_chunk:
        chunks.append(current_chunk)
    
    for chunk in chunks:
        try:
            escaped_chunk = escape_markdown_v2(chunk.strip())
            await message.answer(escaped_chunk, parse_mode="MarkdownV2")
        except Exception as e:
            # Fallback to plain text if markdown fails
            logger.warning(f"Markdown parsing failed, sending as plain text: {e}")
            await message.answer(chunk.strip())
        
        await asyncio.sleep(0.1)

@router.message()
async def handle_text_query(message: types.Message):
    user_text = message.text.lower() if message.text else ""
    logger.info(f"User {message.from_user.id} sent: {user_text}")

    # Check if the message is a greeting
    if user_text in GREETINGS:
        greeting_response = "👋 Hey Cloud Guru! I'm your cloud computing assistant. How may I help you today? I can assist with:\n\n" \
                          "• AWS deployments\n" \
                          "• Kubernetes setup\n" \
                          "• CI/CD pipelines\n" \
                          "• Serverless architectures\n" \
                          "• Cloud infrastructure\n" \
                          "• DevOps practices\n\n" \
                          "Just ask your question and I'll provide detailed guidance! 🚀"
        await message.answer(greeting_response)
        return

    try:
        response = await get_cloud_solution(user_text)  
        await send_chunked_response(message, response)
    except Exception as e:
        logger.error(f"Error handling user query: {e}")
        await message.answer("An error occurred while processing your request.")