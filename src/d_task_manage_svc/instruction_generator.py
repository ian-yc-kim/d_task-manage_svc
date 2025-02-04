import asyncio
import logging
from src.d_task_manage_svc.ai_agent import generate_ai_instructions


async def generate_instructions(task_title: str, task_description: str) -> list:
    """Generates instructions by delegating to the AI agent module.

    Args:
        task_title (str): The title of the task.
        task_description (str): The detailed description of the task.

    Returns:
        list: A list of 3-10 concise, single-sentence instructions, or an empty list on failure.
    """
    try:
        instructions = await generate_ai_instructions(task_title, task_description)
        # Validate that the instructions list is within the expected range and format
        if isinstance(instructions, list) and 3 <= len(instructions) <= 10 and all(isinstance(inst, str) and inst.strip() for inst in instructions):
            return instructions
        else:
            logging.error("Invalid instructions format returned from ai_agent.")
            return []
    except Exception as e:
        logging.error(e, exc_info=True)
        return []
