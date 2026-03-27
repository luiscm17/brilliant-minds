import json
import redis.asyncio as redis
from agent_framework import BaseHistoryProvider, AgentSession
from src.config.settings import RedisSettings

redis_url = RedisSettings.get_redis_url()


class RedisHistoryProvider(BaseHistoryProvider):
    """Persist chat history using Redis to keep session context available."""

    def __init__(self, redis_url: str = redis_url):
        self.client = redis.from_url(redis_url)

    async def provide_chat_history(self, session: AgentSession):
        """Return the stored message list for the provided session."""
        key = f"tdh:history:{session.session_id}"
        data = await self.client.get(key)
        if data:
            return json.loads(data)
        return []

    async def store_chat_history(self, session: AgentSession, messages):
        """Save the current message list back into Redis."""
        key = f"tdh:history:{session.session_id}"
        await self.client.set(key, json.dumps(messages))
