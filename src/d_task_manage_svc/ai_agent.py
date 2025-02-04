import os
import logging
from typing import List

import httpx

# Load external configuration for API, values should be managed securely
_API_URL: str = os.environ['GPT4O_API_URL']
# API token for authentication; ensure secure management of credentials
_API_TOKEN: str = os.environ['GPT4O_API_TOKEN']


async def generate_ai_instructions(task_title: str, task_description: str) -> List[str]:
    """Generate a list of concise, single-sentence instructions using the GPT-4O API.

    Args:
        task_title (str): The title of the task. Must not be empty or whitespace.
        task_description (str): The description of the task. Must not be empty or whitespace.

    Returns:
        List[str]: A list of instructions if successful (3 to 10 items), otherwise an empty list.
    """
    # Validate input: task title and description must not be empty/whitespace
    if not task_title.strip() or not task_description.strip():
        logging.error("Task title or task description is empty or whitespace.")
        return []

    payload = {
        "task_title": task_title,
        "task_description": task_description
    }
    headers = {"Authorization": f"Bearer {_API_TOKEN}"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            # Validate response: must be a list of strings, each non-empty and in single-sentence format
            if isinstance(data, list) and all(isinstance(item, str) and item.strip() for item in data):
                # Additional validation: each instruction should be a single sentence (at most one period) and trimmed
                for instr in data:
                    # Count periods; allow exactly one if it ends with a period, or zero if no punctuation
                    period_count = instr.count('.')
                    if period_count > 1:
                        logging.error("Invalid instruction format: Multiple sentences detected. Data: %s", data)
                        return []
                if 3 <= len(data) <= 10:
                    return [item.strip() for item in data]
            logging.error("Invalid response format or instruction count not in range [3-10]. Response: %s", data)
    except Exception as e:
        logging.error(e, exc_info=True)
    return []
