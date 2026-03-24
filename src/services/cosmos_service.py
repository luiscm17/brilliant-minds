"""Azure Cosmos DB service for user profiles, document metadata, and chats."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError

from src.config.settings import CosmosDBSettings
from src.models.schemas import UserProfile, UserProfileUpdate

_cosmos_client: CosmosClient | None = None


def _client() -> CosmosClient:
    global _cosmos_client
    if _cosmos_client is None:
        CosmosDBSettings.validate()
        _cosmos_client = CosmosClient(
            CosmosDBSettings.ENDPOINT, credential=CosmosDBSettings.KEY
        )
    return _cosmos_client


def _db(client: CosmosClient):
    return client.get_database_client(CosmosDBSettings.DATABASE)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_profile_fields() -> dict:
    return {
        "profile_completed": False,
        "has_adhd": False,
        "has_dyslexia": False,
        "reading_level": "A2",
        "preset": "custom",
        "max_sentence_length": 12,
        "tone": "calm_supportive",
        "priorities": ["focus", "calm"],
        "avoid_words": [],
        "fatigue_history": [],
    }


async def get_user_record(user_id: str) -> Optional[dict]:
    container = _db(_client()).get_container_client(CosmosDBSettings.USERS_CONTAINER)
    try:
        return await container.read_item(item=user_id, partition_key=user_id)
    except CosmosResourceNotFoundError:
        return None


async def get_user_profile(user_id: str) -> Optional[UserProfile]:
    item = await get_user_record(user_id)
    if not item or not item.get("profile_completed", False):
        return None
    return _item_to_profile(item)


async def get_user_by_email(email: str) -> Optional[dict]:
    container = _db(_client()).get_container_client(CosmosDBSettings.USERS_CONTAINER)
    query = "SELECT * FROM c WHERE c.email = @email"
    params = [{"name": "@email", "value": email}]
    results = [
        item async for item in container.query_items(query=query, parameters=params)
    ]
    return results[0] if results else None


async def create_user_profile(
    user_id: str, email: str, name: str, hashed_password: str
) -> dict:
    item = {
        "id": user_id,
        "user_id": user_id,
        "email": email,
        "name": name,
        "hashed_password": hashed_password,
        "created_at": _utcnow(),
        **_default_profile_fields(),
    }
    container = _db(_client()).get_container_client(CosmosDBSettings.USERS_CONTAINER)
    await container.create_item(item)
    return item


async def update_user_profile(
    user_id: str, updates: UserProfileUpdate
) -> Optional[UserProfile]:
    container = _db(_client()).get_container_client(CosmosDBSettings.USERS_CONTAINER)
    try:
        item = await container.read_item(item=user_id, partition_key=user_id)
    except CosmosResourceNotFoundError:
        return None

    patch = updates.model_dump(exclude_none=True, by_alias=False)
    item.update(patch)
    item["profile_completed"] = True
    await container.replace_item(item=user_id, body=item)
    return _item_to_profile(item)


def _item_to_profile(item: dict) -> UserProfile:
    return UserProfile(
        hasAdhd=item.get("has_adhd", False),
        hasDyslexia=item.get("has_dyslexia", False),
        readingLevel=item.get("reading_level", "A2"),
        preset=item.get("preset", "custom"),
        maxSentenceLength=item.get("max_sentence_length", 12),
        tone=item.get("tone", "calm_supportive"),
        priorities=item.get("priorities", ["focus", "calm"]),
    )


async def save_document_metadata(
    document_id: str,
    user_id: str,
    filename: str,
    blob_url: Optional[str],
    blob_name: Optional[str],
    status: str,
) -> dict:
    item = {
        "id": document_id,
        "document_id": document_id,
        "user_id": user_id,
        "filename": filename,
        "blob_url": blob_url,
        "blob_name": blob_name,
        "status": status,
        "uploaded_at": _utcnow(),
    }
    container = _db(_client()).get_container_client(CosmosDBSettings.DOCUMENTS_CONTAINER)
    await container.create_item(item)
    return item


async def list_user_documents(user_id: str) -> list[dict]:
    container = _db(_client()).get_container_client(CosmosDBSettings.DOCUMENTS_CONTAINER)
    query = "SELECT * FROM c WHERE c.user_id = @user_id ORDER BY c.uploaded_at DESC"
    params = [{"name": "@user_id", "value": user_id}]
    return [item async for item in container.query_items(query=query, parameters=params)]


async def get_document_metadata(document_id: str, user_id: str) -> Optional[dict]:
    container = _db(_client()).get_container_client(CosmosDBSettings.DOCUMENTS_CONTAINER)
    query = "SELECT * FROM c WHERE c.document_id = @document_id AND c.user_id = @user_id"
    params = [
        {"name": "@document_id", "value": document_id},
        {"name": "@user_id", "value": user_id},
    ]
    results = [item async for item in container.query_items(query=query, parameters=params)]
    return results[0] if results else None


async def update_document_status(
    document_id: str,
    user_id: str,
    status: str,
) -> Optional[dict]:
    container = _db(_client()).get_container_client(CosmosDBSettings.DOCUMENTS_CONTAINER)
    query = "SELECT * FROM c WHERE c.document_id = @document_id AND c.user_id = @user_id"
    params = [
        {"name": "@document_id", "value": document_id},
        {"name": "@user_id", "value": user_id},
    ]
    results = [item async for item in container.query_items(query=query, parameters=params)]
    if not results:
        return None

    item = results[0]
    item["status"] = status
    await container.replace_item(item=item["id"], body=item, partition_key=user_id)
    return item


async def delete_document_metadata(document_id: str, user_id: str) -> None:
    container = _db(_client()).get_container_client(CosmosDBSettings.DOCUMENTS_CONTAINER)
    try:
        await container.delete_item(item=document_id, partition_key=user_id)
    except CosmosResourceNotFoundError:
        pass


async def list_user_chats(user_id: str) -> list[dict]:
    container = _db(_client()).get_container_client(CosmosDBSettings.CHATS_CONTAINER)
    query = "SELECT * FROM c WHERE c.user_id = @user_id ORDER BY c.created_at DESC"
    params = [{"name": "@user_id", "value": user_id}]
    return [item async for item in container.query_items(query=query, parameters=params)]


async def update_chat_title(chat_id: str, user_id: str, title: str) -> Optional[dict]:
    container = _db(_client()).get_container_client(CosmosDBSettings.CHATS_CONTAINER)
    query = "SELECT * FROM c WHERE c.id = @id AND c.user_id = @user_id"
    params = [{"name": "@id", "value": chat_id}, {"name": "@user_id", "value": user_id}]
    results = [item async for item in container.query_items(query=query, parameters=params)]
    if not results:
        return None
    item = results[0]
    item["title"] = title
    await container.replace_item(item=item["id"], body=item, partition_key=user_id)
    return item


async def delete_chat(chat_id: str, user_id: str) -> bool:
    container = _db(_client()).get_container_client(CosmosDBSettings.CHATS_CONTAINER)
    query = "SELECT * FROM c WHERE c.id = @id AND c.user_id = @user_id"
    params = [{"name": "@id", "value": chat_id}, {"name": "@user_id", "value": user_id}]
    results = [item async for item in container.query_items(query=query, parameters=params)]
    if not results:
        return False
    await container.delete_item(item=results[0]["id"], partition_key=user_id)
    return True


async def create_chat(user_id: str, title: Optional[str]) -> dict:
    item = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": title or "Hackathon demo",
        "created_at": _utcnow(),
    }
    container = _db(_client()).get_container_client(CosmosDBSettings.CHATS_CONTAINER)
    await container.create_item(item)
    return item


async def create_share(user_id: str, data: dict) -> str:
    share_token = str(uuid.uuid4())
    item = {
        "id": share_token,
        "user_id": "public",
        "owner_id": user_id,
        "data": data,
        "created_at": _utcnow(),
    }
    db = _db(_client())
    try:
        container = db.get_container_client(CosmosDBSettings.SHARES_CONTAINER)
        await container.create_item(item)
    except Exception:
        await db.create_container_if_not_exists(
            id=CosmosDBSettings.SHARES_CONTAINER,
            partition_key={"paths": ["/user_id"], "kind": "Hash"},
        )
        container = db.get_container_client(CosmosDBSettings.SHARES_CONTAINER)
        await container.create_item(item)
    return share_token


async def get_share(share_token: str) -> Optional[dict]:
    try:
        container = _db(_client()).get_container_client(CosmosDBSettings.SHARES_CONTAINER)
        item = await container.read_item(item=share_token, partition_key="public")
        return item.get("data")
    except Exception:
        return None


async def save_progress(user_id: str, reading_level: str, preset: str) -> None:
    container = _db(_client()).get_container_client(CosmosDBSettings.USERS_CONTAINER)
    try:
        item = await container.read_item(item=user_id, partition_key=user_id)
        history: list[dict] = item.get("fatigue_history", [])
        history.append(
            {
                "date": _utcnow(),
                "level": reading_level,
                "preset": preset,
            }
        )
        item["fatigue_history"] = history[-50:]
        await container.replace_item(item=user_id, body=item)
    except Exception:
        pass
