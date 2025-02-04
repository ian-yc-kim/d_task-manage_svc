import asyncio
import logging

async def generate_ai_instructions(task_title: str, task_description: str) -> list:
    """Generate a list of concise instructions based on task title and description.
    Returns a list of 3-10 single-sentence instructions. In case of an error, returns an empty list.
    """
    try:
        # Simulate instruction generation logic. In a real scenario, this might call an external LLM API asynchronously.
        instructions = [
            f"Review the task: {task_title}.",
            "Validate all inputs for consistency.",
            "Implement the changes per the specifications provided."
        ]
        # Ensure we always have between 3 and 10 instructions.
        if len(instructions) < 3:
            instructions.append("Perform additional reviews as necessary.")
        elif len(instructions) > 10:
            instructions = instructions[:10]
        return instructions
    except Exception as e:
        logging.error(e, exc_info=True)
        return []
