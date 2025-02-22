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
            "query": "How do I deploy an application on AWS?",
            "context": "Explain step-by-step using best DevOps practices, covering scalability, security, and cost optimization."
        },
        "k8s_setup": {
            "query": "How do I set up a Kubernetes cluster?",
            "context": "Guide me through a production-ready Kubernetes setup, focusing on security, autoscaling, and monitoring."
        },
        "cicd": {
            "query": "How do I configure a CI/CD pipeline?",
            "context": "Provide a professional-level guide on automating deployments, ensuring security, and implementing best practices."
        },
        "serverless": {
            "query": "How do I deploy a serverless function?",
            "context": "Explain serverless architecture using AWS Lambda, focusing on monitoring, security, and performance."
        }
    }

    task = callback_query.data
    if task in cloud_prompts:
        await callback_query.answer()  

        task_info = cloud_prompts[task]
        enhanced_query = f"""
        You are a professional cloud computing expert and chatbot. 
        Your task is to assist users by providing **detailed, production-ready solutions**.
        
        **User Query:** {task_info['query']}  
        **Context:** {task_info['context']}  
        
        Be interactive, provide step-by-step instructions, suggest best practices, and engage users as a knowledgeable assistant.
        """

        try:
            response = await get_cloud_solution(enhanced_query)  
            await send_chunked_response(callback_query.message, response)
            logger.info(f"User {callback_query.from_user.id} received an expert response for {task}")
        except Exception as e:
            logger.error(f"Error processing cloud task: {e}")
            await callback_query.message.answer("⚠️ Sorry, an error occurred while processing your request.")

def escape_markdown_v2(text: str) -> str:
    """Escapes special characters for Telegram's MarkdownV2 format."""
    chars_to_escape = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in chars_to_escape:
        text = text.replace(char, f'\\{char}')
    return text

async def send_chunked_response(message: types.Message, response: str, chunk_size=4000):
    """Splits long responses into chunks and sends them sequentially."""
    chunks = []
    current_chunk = ""
    
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
            logger.warning(f"Markdown parsing failed, sending as plain text: {e}")
            await message.answer(chunk.strip())
        
        await asyncio.sleep(0.1)

@router.message()
async def handle_text_query(message: types.Message):
    """Handles user messages and provides AI-powered responses."""
    user_text = message.text.lower() if message.text else ""
    logger.info(f"User {message.from_user.id} sent: {user_text}")

    if user_text in GREETINGS:
        greeting_response = """
        👋 Hey Cloud Guru! I'm **Zephyr CloudBot**, your expert in cloud computing.  
        
        🔹 Need help with AWS, Kubernetes, CI/CD, or DevOps?  
        🔹 Ask me any **cloud-related** question, and I'll provide **detailed guidance**.  
        🔹 Just type your query, and let's build something great together! 🚀  
        """
        await message.answer(greeting_response)
        return

    try:
        enhanced_query = f"""
        You are **Zephyr CloudBot**, a highly interactive and professional cloud computing expert.
        Your goal is to help users **solve cloud-related problems with clear, engaging responses**.

        **User Query:** {user_text}  
        **Context:** Provide a **detailed, step-by-step solution**, best practices, and practical insights.

        Maintain a conversational and engaging tone while ensuring **technical accuracy**.
        """
        
        response = await get_cloud_solution(enhanced_query)
        await send_chunked_response(message, response)
    except Exception as e:
        logger.error(f"Error handling user query: {e}")
        await message.answer("⚠️ An error occurred while processing your request. Please try again.")

