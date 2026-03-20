"""Azure Cosmos DB service for user profiles, documents metadata and chats."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError

from src.config.settings import CosmosDBSettings
from src.models.schemas import UserProfile, UserProfileUpdate


def _client() -> CosmosClient:
    CosmosDBSettings.validate()
    return CosmosClient(CosmosDBSettings.ENDPOINT, credential=CosmosDBSettings.KEY)


# ---------------------------------------------------------------------------
# User profiles
# ---------------------------------------------------------------------------

async def get_user_profile(user_id: str) -> Optional[UserProfile]:
    async with _client() as client:
        container = client.get_database_client(CosmosDBSettings.DATABASE).get_container_client(
            CosmosDBSettings.USERS_CONTAINER
        )
        try:
            item = await container.read_item(item=user_id, partition_key=user_id)
            return _item_to_profile(item)
        except CosmosResourceNotFoundError:
            return None


async def get_user_by_email(email: str) -> Optional[dict]:
    async with _client() as client:
        container = client.get_database_client(CosmosDBSettings.DATABASE).get_container_client(
            CosmosDBSettings.USERS_CONTAINER
        )
        query = "SELECT * FROM c WHERE c.email = @email"
        params = [{"name": "@email", "value": email}]
        results = [item async for item in container.query_items(query=query, parameters=params)]
        return results[0] if results else None


async def create_user_profile(user_id: str, email: str, name: str, hashed_password: str) -> UserProfile:
    now = datetime.now(timezone.utc).isoformat()
    item = {
        "id": user_id,
        "user_id": user_id,
        "email": email,
        "name": name,
        "hashed_password": hashed_password,
        "reading_level": "A2",
        "max_sentence_length": 12,
        "tone": "calm_supportive",
        "avoid_words": [],
        "preset": "TDAH",
        "fatigue_history": [],
        "created_at": now,
    }
    async with _client() as client:
        container = client.get_database_client(CosmosDBSettings.DATABASE).get_container_client(
            CosmosDBSettings.USERS_CONTAINER
        )
        await container.create_item(item)
    return _item_to_profile(item)


async def update_user_profile(user_id: str, updates: UserProfileUpdate) -> Optional[UserProfile]:
    async with _client() as client:
        container = client.get_database_client(CosmosDBSettings.DATABASE).get_container_client(
            CosmosDBSettings.USERS_CONTAINER
        )
        try:
            item = await container.read_item(item=user_id, partition_key=user_id)
        except CosmosResourceNotFoundError:
            return None

        patch = updates.model_dump(exclude_none=True)
        item.update(patch)
        await container.replace_item(item=user_id, body=item)
        return _item_to_profile(item)


def _item_to_profile(item: dict) -> UserProfile:
    return UserProfile(
        id=item["id"],
        user_id=item["user_id"],
        email=item["email"],
        name=item["name"],
        reading_level=item.get("reading_level", "A2"),
        max_sentence_length=item.get("max_sentence_length", 12),
        tone=item.get("tone", "calm_supportive"),
        avoid_words=item.get("avoid_words", []),
        preset=item.get("preset", "TDAH"),
        fatigue_history=item.get("fatigue_history", []),
        created_at=item.get("created_at"),
    )


# ---------------------------------------------------------------------------
# Documents metadata
# ---------------------------------------------------------------------------

async def save_document_metadata(
    document_id: str, user_id: str, filename: str, blob_url: str
) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    item = {
        "id": document_id,
        "document_id": document_id,
        "user_id": user_id,
        "filename": filename,
        "blob_url": blob_url,
        "status": "indexed",
        "uploaded_at": now,
    }
    async with _client() as client:
        container = client.get_database_client(CosmosDBSettings.DATABASE).get_container_client(
            CosmosDBSettings.DOCUMENTS_CONTAINER
        )
        await container.create_item(item)
    return item


async def list_user_documents(user_id: str) -> list[dict]:
    async with _client() as client:
        container = client.get_database_client(CosmosDBSettings.DATABASE).get_container_client(
            CosmosDBSettings.DOCUMENTS_CONTAINER
        )
        query = "SELECT * FROM c WHERE c.user_id = @user_id ORDER BY c.uploaded_at DESC"
        params = [{"name": "@user_id", "value": user_id}]
        return [item async for item in container.query_items(query=query, parameters=params)]


async def delete_document_metadata(document_id: str, user_id: str) -> None:
    async with _client() as client:
        container = client.get_database_client(CosmosDBSettings.DATABASE).get_container_client(
            CosmosDBSettings.DOCUMENTS_CONTAINER
        )
        try:
            await container.delete_item(item=document_id, partition_key=user_id)
        except CosmosResourceNotFoundError:
            pass


# ---------------------------------------------------------------------------
# Chats
# ---------------------------------------------------------------------------

async def create_chat(user_id: str, title: Optional[str]) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    item = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": title or "New chat",
        "created_at": now,
    }
    async with _client() as client:
        container = client.get_database_client(CosmosDBSettings.DATABASE).get_container_client(
            CosmosDBSettings.CHATS_CONTAINER
        )
        await container.create_item(item)
    return item
