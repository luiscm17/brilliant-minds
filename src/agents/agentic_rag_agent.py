"""Agentic RAG Agent — decides autonomously when and what to search.

Instead of a static top-k retrieval before the LLM call, this agent has
access to a `search_documents` tool and calls it as many times as needed
(up to MAX_ITERATIONS) before producing the final simplified text.
"""

import json
from typing import Optional

from openai import AsyncAzureOpenAI

from src.config.settings import OpenAISettings
from src.services import search_service
from src.agents.simplifier_agent import LEVEL_RULES, PRESET_EXTRA

MAX_ITERATIONS = 4  # safety cap on search rounds


class AgenticRAGAgent:
    """Simplifier agent that retrieves its own context via tool calling."""

    _TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "search_documents",
                "description": (
                    "Search the user's uploaded documents for relevant sections. "
                    "Call this whenever you need specific content to simplify or answer the request. "
                    "You can call it multiple times with different queries to gather all needed context."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Specific query to find relevant document sections",
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of chunks to retrieve (1-5, default 3)",
                            "default": 3,
                        },
                    },
                    "required": ["query"],
                },
            },
        }
    ]

    def __init__(self, user_id: str):
        self._user_id = user_id
        self._client = AsyncAzureOpenAI(
            azure_endpoint=OpenAISettings.ENDPOINT or "",
            api_key=OpenAISettings.API_KEY or "",
            api_version="2024-08-01-preview",
        )
        self._model = OpenAISettings.CHAT_MODEL

    async def run(
        self,
        message: str,
        reading_level: str,
        preset: str,
        avoid_words: list[str],
        target_language: Optional[str] = None,
    ) -> tuple[str, list[str]]:
        """Run agentic loop. Returns (simplified_text, list_of_queries_made)."""

        avoid = ", ".join(avoid_words) if avoid_words else "none"
        lang_instruction = (
            f"Output the simplified text in {target_language}."
            if target_language
            else "Detect the source language and respond in the SAME language."
        )

        system_prompt = (
            "You are a Plain Language specialist with access to a document search tool.\n"
            "Your job:\n"
            "1. Use search_documents to find relevant sections from the user's documents.\n"
            "2. Search as many times as needed to gather sufficient context.\n"
            "3. Once you have enough context, produce the simplified text.\n\n"
            f"Reading level: {reading_level}. Rules: {LEVEL_RULES.get(reading_level, '')}\n"
            f"Preset style: {PRESET_EXTRA.get(preset, '')}\n"
            f"Never use these words: {avoid}\n"
            f"{lang_instruction}\n"
            "Output ONLY the simplified text — no preamble, no meta-commentary."
        )

        messages: list[dict] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]

        queries_made: list[str] = []

        for _ in range(MAX_ITERATIONS):
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                tools=self._TOOLS,
                tool_choice="auto",
                temperature=0.3,
            )

            choice = response.choices[0]

            # Agent wants to call a tool
            if choice.finish_reason == "tool_calls":
                tool_calls = choice.message.tool_calls or []
                # Append assistant message with tool_calls
                messages.append({
                    "role": "assistant",
                    "content": choice.message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in tool_calls
                    ],
                })

                # Execute each tool call
                for tc in tool_calls:
                    if tc.function.name == "search_documents":
                        args = json.loads(tc.function.arguments)
                        query = args.get("query", message)
                        top_k = min(int(args.get("top_k", 3)), 5)
                        queries_made.append(query)

                        try:
                            chunks = await search_service.search_context(
                                query, self._user_id, top_k=top_k
                            )
                            content = "\n\n---\n\n".join(chunks) if chunks else "No relevant content found."
                        except Exception:
                            content = "Search unavailable."

                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": content,
                        })

            else:
                # Agent finished — return the simplified text
                return choice.message.content or "", queries_made

        # Fallback if max iterations reached without a final answer
        fallback = await self._client.chat.completions.create(
            model=self._model,
            messages=messages + [{"role": "user", "content": "Now produce the simplified text."}],
            temperature=0.3,
        )
        return fallback.choices[0].message.content or "", queries_made
