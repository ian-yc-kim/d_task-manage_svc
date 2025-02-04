import pytest
import asyncio
from src.d_task_manage_svc import instruction_generator


@pytest.mark.asyncio
async def test_generate_instructions_success(monkeypatch):
    async def mock_generate_ai_instructions(task_title, task_description):
        return [
            "Instruction one.",
            "Instruction two.",
            "Instruction three."
        ]
    
    # Monkeypatch the generate_ai_instructions method in the ai_agent module
    monkeypatch.setattr(instruction_generator, 'generate_ai_instructions', mock_generate_ai_instructions)
    
    instructions = await instruction_generator.generate_instructions("Sample Task", "This is a sample description.")
    assert isinstance(instructions, list)
    assert len(instructions) == 3
    for instruction in instructions:
        assert isinstance(instruction, str)
        assert instruction.strip()


@pytest.mark.asyncio
async def test_generate_instructions_failure(monkeypatch):
    async def mock_generate_ai_instructions_fail(task_title, task_description):
        raise Exception("Simulated failure")
    
    monkeypatch.setattr(instruction_generator, 'generate_ai_instructions', mock_generate_ai_instructions_fail)
    
    instructions = await instruction_generator.generate_instructions("Sample Task", "This is a sample description.")
    assert instructions == []
