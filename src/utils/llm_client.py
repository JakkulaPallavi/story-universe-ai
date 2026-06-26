"""
Anthropic API wrapper with JSON-structured output support.
"""
import json
import re
from typing import Any
import anthropic
from config import Config


class LLMClient:
    """
    Thin wrapper around the Anthropic client.
    Provides a clean interface for agents to call Claude
    and automatically parse JSON responses.
    """

    def __init__(self, config: Config):
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
    ) -> str:
        """Generate a plain text response."""
        message = self.client.messages.create(
            model=self.config.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
    ) -> Any:
        """
        Generate a response and parse it as JSON.
        Strips markdown code fences if present.
        """
        full_system = (
            system_prompt
            + "\n\nCRITICAL: Respond ONLY with valid JSON. "
            "No preamble, no explanation, no markdown fences. "
            "Raw JSON only."
        )
        raw = self.generate(full_system, user_prompt, max_tokens)
        return self._parse_json(raw)

    @staticmethod
    def _parse_json(text: str) -> Any:
        """Parse JSON, stripping markdown fences if needed."""
        text = text.strip()
        # Strip ```json ... ``` or ``` ... ```
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM returned invalid JSON:\n{text[:500]}\n\nError: {e}")
