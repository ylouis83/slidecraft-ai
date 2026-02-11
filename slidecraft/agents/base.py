"""
Base Agent class for SlideCraft agents.
All agents inherit from this base and share a common structure.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel

from slidecraft.config import SlideCraftConfig
from slidecraft.utils.llm_client import get_llm

logger = logging.getLogger("slidecraft")


class BaseAgent(ABC):
    """Base class for all SlideCraft agents.

    Each agent encapsulates:
    - A system prompt defining its role and expertise
    - Access to an LLM client
    - Structured output parsing
    """

    name: str = "base_agent"
    description: str = "Base agent"

    def __init__(self, config: SlideCraftConfig):
        self.config = config
        self._llm: Optional[BaseChatModel] = None

    @property
    def llm(self) -> BaseChatModel:
        if self._llm is None:
            self._llm = get_llm(self.config)
        return self._llm

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt defining this agent's role."""
        ...

    async def invoke(self, user_message: str, images: list[str] | None = None) -> str:
        """Invoke the agent with a text message and optional images.

        Args:
            user_message: The user/orchestrator message to the agent.
            images: Optional list of base64-encoded image strings or URLs.

        Returns:
            The raw text response from the LLM.
        """
        messages = [SystemMessage(content=self.system_prompt)]

        # Build multimodal content if images provided
        if images:
            content: list[dict[str, Any]] = [{"type": "text", "text": user_message}]
            for img in images:
                if img.startswith("http"):
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": img},
                    })
                else:
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img}"},
                    })
            messages.append(HumanMessage(content=content))
        else:
            messages.append(HumanMessage(content=user_message))

        response = await self.llm.ainvoke(messages)
        return str(response.content)

    async def invoke_structured(
        self,
        user_message: str,
        output_schema: type,
        images: list[str] | None = None,
    ) -> Any:
        """Invoke the agent and parse the response into a Pydantic model.

        The agent is instructed to return valid JSON conforming to the schema.
        """
        schema_json = json.dumps(output_schema.model_json_schema(), indent=2, ensure_ascii=False)
        structured_prompt = (
            f"{user_message}\n\n"
            f"请以 JSON 格式返回结果，严格符合以下 schema：\n"
            f"```json\n{schema_json}\n```\n"
            f"只返回 JSON，不要包含其他任何内容。"
        )

        raw = await self.invoke(structured_prompt, images=images)

        # Extract JSON from possible markdown code block
        raw = raw.strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            # Remove first and last ``` lines
            json_lines = []
            in_block = False
            for line in lines:
                if line.strip().startswith("```") and not in_block:
                    in_block = True
                    continue
                if line.strip() == "```" and in_block:
                    break
                if in_block:
                    json_lines.append(line)
            raw = "\n".join(json_lines)

        try:
            data = json.loads(raw)
            return output_schema.model_validate(data)
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"[{self.name}] Failed to parse structured output: {e}")
            logger.debug(f"[{self.name}] Raw response: {raw[:500]}")
            raise

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
