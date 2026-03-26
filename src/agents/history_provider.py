# agents/redis_history_provider.py
import json
import redis.asyncio as redis
from agent_framework import BaseHistoryProvider, AgentSession
from src.config.settings import RedisSettings

redis_url = RedisSettings.get_redis_url()

class RedisHistoryProvider(BaseHistoryProvider):
    def __init__(self, redis_url: str = redis_url):
        self.client = redis.from_url(redis_url)

    async def provide_chat_history(self, session_id: AgentSession):
        key = f"history:{session_id}"
        data = await self.client.get(key)
        if data:
            return json.loads(data)
        return []

    async def store_chat_history(self, session_id: AgentSession, messages):
        key = f"history:{session_id}"
        await self.client.set(key, json.dumps(messages))