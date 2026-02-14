"""
CodeGenie AI Editor — Gemini AI Service
Wrapper around google-genai SDK for interacting with Gemini.
"""

from google import genai
from app.core.config import settings


class AIService:
    """Service class for interacting with Google Gemini AI."""

    def __init__(self):
        """Initialize the Gemini client with API key from settings."""
        self._client = None
        self._model = settings.gemini_model

    @property
    def client(self) -> genai.Client:
        """Lazy-initialize the Gemini client."""
        if self._client is None:
            self._client = genai.Client(api_key=settings.gemini_api_key)
        return self._client

    async def generate_response(
        self,
        message: str,
        context: str | None = None,
        system_prompt: str | None = None,
    ) -> str:
        """
        Generate a response from Gemini.

        Args:
            message: The user's message/prompt.
            context: Optional code context to include.
            system_prompt: Optional system instruction.

        Returns:
            The AI-generated response text.
        """
        # Build the full prompt
        parts = []

        if system_prompt:
            parts.append(system_prompt)

        if context:
            parts.append(f"Code Context:\n```\n{context}\n```")

        parts.append(message)
        full_prompt = "\n\n".join(parts)

        # Call Gemini (synchronous SDK call)
        response = self.client.models.generate_content(
            model=self._model,
            contents=full_prompt,
        )

        return response.text

    async def chat_completion(
        self,
        message: str,
        context: str | None = None,
    ) -> str:
        """
        Generate a chat completion with CodeGenie's system prompt.

        Args:
            message: The user's message.
            context: Optional code context.

        Returns:
            The AI response text.
        """
        system_prompt = (
            "You are CodeGenie, an AI-powered coding assistant. "
            "You help developers write, debug, refactor, and understand code. "
            "Be concise, accurate, and provide code examples when helpful. "
            "If code context is provided, use it to give more relevant answers."
        )

        return await self.generate_response(
            message=message,
            context=context,
            system_prompt=system_prompt,
        )


# Singleton instance
ai_service = AIService()
