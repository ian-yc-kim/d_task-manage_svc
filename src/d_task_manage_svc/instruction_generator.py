import logging
from typing import List, Optional

import httpx


async def generate_instructions(task_title: str, task_description: str) -> Optional[List[str]]:
    """Generate instructions asynchronously via GPT-4 API for the given task details.

    Args:
        task_title (str): The title of the task.
        task_description (str): The detailed description of the task.

    Returns:
        Optional[List[str]]: A list of concise instructions if the API call succeeds; otherwise, None.
    """
    url = "https://api.gpt4.example.com/generate"  # Placeholder URL for GPT-4 API endpoint
    payload = {
        "task_title": task_title,
        "task_description": task_description
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            instructions = data.get("instructions")

            if isinstance(instructions, list):
                return instructions
            elif isinstance(instructions, str):
                # Split by period and clean up, ensuring each is a non-empty sentence
                return [instr.strip() for instr in instructions.split('.') if instr.strip()]
            else:
                return None
    except Exception as e:
        logging.error(e, exc_info=True)
        return None
