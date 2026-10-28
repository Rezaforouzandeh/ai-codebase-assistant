import os

from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()

client = AsyncAnthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"]
)


async def generate_response(prompt: str) -> str:

    response = await client.messages.create(
        model=os.environ["CLAUDE_MODEL"],
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return "".join(
        block.text
        for block in response.content
        if block.type == "text"
    )