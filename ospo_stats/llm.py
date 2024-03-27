import json

from anthropic import Anthropic


def create_messages_for_categorization(
    readme: str,
    options: list[str] | None = None,
    allow_extra: bool = True,
    trim_to: int = 500,
) -> list:
    """Create Anthropic prompt for categorizing readme content."""

    if len(readme) > trim_to:
        readme = readme[:trim_to] + "..."

    if options is None:
        options = ["Software", "Course Material"]

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
                    "text": f"Categorize below readme content as one of these options: {options_prompt}. Use JSON format with the key: category. {allow_extra_prompt if allow_extra else ''}\n <readme>{readme}</readme>",
                }
            ],
        }
    ]


def get_category(
    readme: str,
    client: Anthropic | None = None,
    model: str = "claude-3-haiku-20240307",
    trim_to: int = 500,
) -> str:
    """Get repo category using Anthropic API."""

    if client is None:
        client = Anthropic()

    response = client.messages.create(
        model=model,
        max_tokens=100,
        temperature=0,
        messages=create_messages_for_categorization(readme, trim_to=trim_to),
    )
    return json.loads(response.content[0].text)["category"]
