import os

from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()


async def generate_response(prompt: str) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("CLAUDE_MODEL")

    if not api_key or not model:
        raise RuntimeError(
            "Claude API configuration is missing"
        )

    async with AsyncAnthropic(api_key=api_key) as client:
        response = await client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

    return "".join(
        block.text
        for block in response.content
        if block.type == "text"
    )