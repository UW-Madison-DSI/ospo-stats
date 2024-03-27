import json
import time

import tenacity
from anthropic import Anthropic


def create_messages_for_categorization(
    text: str,
    options: list[str] | None = None,
    allow_extra: bool = True,
    trim_to: int = 500,
) -> list:
    """Create Anthropic prompt for categorizing readme content."""

    if len(text) > trim_to:
        text = text[:trim_to] + "..."

    if options is None:
        options = ["Software", "Course Material", "Website", "Assignment"]

    options_prompt = ", ".join(f"{option}" for i, option in enumerate(options, start=1))
    allow_extra_prompt = (
        "If none of the options fits the content, come up with a new category."
    )
    return [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Categorize below readme content as one of these options: {options_prompt}. Use JSON format with the key: category. {allow_extra_prompt if allow_extra else ''}\n <readme>{text}</readme>",
                }
            ],
        }
    ]


@tenacity.retry(
    wait=tenacity.wait_exponential(),
    stop=tenacity.stop_after_attempt(5),
)
def get_category(
    text: str,
    client: Anthropic | None = None,
    model: str = "claude-3-haiku-20240307",
    trim_to: int = 500,
    sleep: int = 1,
) -> str:
    """Get repo category using Anthropic API."""

    if client is None:
        client = Anthropic()

    response = client.messages.create(
        model=model,
        max_tokens=100,
        temperature=0,
        messages=create_messages_for_categorization(text, trim_to=trim_to),
    )
    if sleep:
        time.sleep(sleep)

    return json.loads(response.content[0].text)["category"]
