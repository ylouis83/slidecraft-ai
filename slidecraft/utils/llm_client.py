"""LLM Client factory — creates the appropriate LangChain LLM based on config."""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel

from slidecraft.config import LLMProvider, SlideCraftConfig


def get_llm(config: SlideCraftConfig) -> BaseChatModel:
    """Create and return an LLM client based on configuration."""
    provider = config.llm.provider

    if provider == LLMProvider.OPENAI:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=config.llm.openai_model,
            api_key=config.llm.openai_api_key,
            temperature=0.7,
            max_tokens=4096,
        )
    elif provider == LLMProvider.ANTHROPIC:
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=config.llm.anthropic_model,
            api_key=config.llm.anthropic_api_key,
            temperature=0.7,
            max_tokens=4096,
        )
    elif provider == LLMProvider.GOOGLE:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=config.llm.google_model,
            google_api_key=config.llm.google_api_key,
            temperature=0.7,
            max_output_tokens=4096,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
