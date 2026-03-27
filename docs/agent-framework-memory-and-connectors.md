# Agent Framework: session state, memory, and persistence strategy

This document collects the key concepts and integration points when you orchestrate agents with Microsoft Agent Framework and want to decide how to manage sessions, history, context, and persistent memory across providers (Azure OpenAI, OpenAI, Foundry).

## Core concepts

- **`AgentSession`** – reuse the same session across `agent.run()` calls to keep the thread identifiers, context state, and any custom context providers intact. Sessions serialize and stay alive until you explicitly close them, so you can safely share them with workflows or middleware.
- **Context providers** – implement `BaseContextProvider`/`BaseHistoryProvider` to push structured instructions before a call and to surface stored data afterwards. A context provider can store JSON in `session.state` (see the Python `UserMemoryProvider` example) or hit an external store of your choosing.
- **History providers** – are also context providers. They can replay chat history when `load_messages=True` and optionally capture every message for auditing when `store_context_messages=True`. Keep only one provider with `load_messages=True` to avoid replay duplication.
- **Middleware and workflows** – workflows (Step 5) rely on the same agent primitives. You can wire context providers into the underlying `Agent` before building workflows, so every workflow step inherits your memory hooks.

## Provider compatibility with persistence

All providers expose the shared `Agent`/`AIAgent` interface, so once you implement context/history providers, they work regardless of the LLM backend.

## Redis-based memory

Microsoft ships `agent-framework-redis` with two pluggable components:

1. **`RedisContextProvider`** – stores structured context rows in Redis (uses RediSearch for full-text queries and optional vector rolling). You can set filters and embeddings so retrieval is scoped per user, thread, or tenant before every run.
2. **`RedisHistoryProvider`** – implements `ChatMessageStoreProtocol` with Redis Lists. Each conversation thread gets a namespaced key (`{key_prefix}:{thread_id}`) so you can trim old messages (LTRIM), TTL them, and even serialize the store for session continuation.

Redis supports both classic connections (`redis_url`) and Azure Managed Redis via `CredentialProvider`. Azure-hosted Redis can live beside Azure OpenAI or Foundry so you keep low-latency persistence near the compute plane. Use the history provider for short-term working memory, and the context provider for selectively searchable, filterable long-term memory.

## Azure Cosmos DB memory

Azure Cosmos DB for NoSQL offers deep support for multi-tier agent memory:

- **Short-term memory**: store the latest `N` turns per thread (partition key = thread ID, tenant+thread, or GUID). TTL can automatically prune working memory, or you can snapshot turns into summaries before archiving.
- **Long-term memory**: persist user preferences, summaries, or retrieval candidates as separate items (one turn per doc or aggregated thread doc). Cosmos supports vectors (DiskANN or quantized indexes) and BM25 full-text search, so you can run hybrid queries that combine lexical matches with semantic similarity.
- **Retrieval patterns**: the document covers queries such as `ORDER BY timestamp DESC`, vector similarity via `VectorDistance`, and hybrid ranking with RRF, letting your context provider prefetch relevant memories before invoking the agent.

Cosmos can also act as a vector store for your own embeddings, and you can point this store into the same context provider pipeline. Because Cosmos is multi-region and fully managed, it pairs especially well with Foundry (which can run on Azure) and with Azure OpenAI agents that already live in the same subscription.

## Recommendations

1. **Keep the same `AgentSession` across calls** so you leverage built-in session state and reuse the context/history providers without rehydrating every run. Sessions serialize/deserialize your providers for workflows and threads, which keeps persistence consistent across returns.
2. **Pair short-term history with Redis or Cosmos**: Redis is the fastest option for high-volume chat history and per-message trimming; Cosmos is better when you need vector/full-text search, TTL, or multi-tenant analytics. You can layer them (Redis for working memory + Cosmos for long-term recall) by adding both providers to the `context_providers` list and setting `load_messages=True` only on the history provider you want to replay.
3. **Choose your provider based on tooling needs**: Azure OpenAI and OpenAI offer the richest hosted tools (code interpreter, MCP), while Foundry provides server-managed agents with optional persistent history. Since the Agent Framework keeps the same interface, you can prototype with one backend and switch by wiring a different client (and the same context providers) when you decide on the production LLM provider.

## Suggested next steps

1. Prototype the `UserMemoryProvider` flow from Step 4, attach Redis or Cosmos, and inspect `session.state` after each run to ensure your custom data persists.
2. Try the Redis history provider sample (see `samples/02-agents/conversations/redis_history_provider.py`) with Azure Managed Redis credentials to measure latency.
3. If you need semantic caching or tenant-aware recall, model Cosmos documents after the “one turn per item” pattern and experiment with hybrid searches before passing the results into your context provider pipeline.

## References

- https://learn.microsoft.com/en-us/agent-framework/get-started/memory
- https://learn.microsoft.com/en-us/agent-framework/agents/providers/azure-openai
- https://learn.microsoft.com/en-us/agent-framework/agents/providers/openai
- https://learn.microsoft.com/en-us/agent-framework/agents/providers/microsoft-foundry
- https://learn.microsoft.com/en-us/python/api/agent-framework-core/agent_framework.redis?view=agent-framework-python-latest
- https://learn.microsoft.com/en-us/azure/cosmos-db/gen-ai/agentic-memories
