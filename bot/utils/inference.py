import asyncio
import time
import requests
from loguru import logger
import aiohttp

from bot.utils.config import API_URL, HF_API_KEY

HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

async def get_cloud_solution(prompt: str) -> str:
    """Asynchronously fetch a cloud solution using an API."""
    data = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1000,
            "temperature": 0.7,
            "top_p": 0.95,
            "repetition_penalty": 1.2
        }
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(API_URL, headers=HEADERS, json=data) as response:
                if response.status == 503:
                    json_response = await response.json()
                    estimated_time = json_response.get('estimated_time', 30)
                    logger.info(f"Model loading, retrying after {estimated_time}s")
                    await asyncio.sleep(estimated_time)  
                    async with session.post(API_URL, headers=HEADERS, json=data) as retry_response:
                        retry_response.raise_for_status()
                        json_result = await retry_response.json()
                        return json_result[0]["generated_text"]

                response.raise_for_status()
                json_result = await response.json()
                return json_result[0]["generated_text"]

        except Exception as e:
            logger.error(f"API Error: {e}")
            return "Error: Unable to generate solution. Please try again."
    
