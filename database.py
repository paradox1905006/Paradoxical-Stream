# database.py (UPDATED VERSION)

import motor.motor_asyncio
from config import Config

class Database:
    def __init__(self):
        self._client = None
        self.db = None
        self.collection = None
        if not Config.DATABASE_URL:
            print("WARNING: DATABASE_URL not set. Links will not be permanent.")

    async def connect(self):
        """Database se connection banata hai."""
        if Config.DATABASE_URL:
            print("Connecting to the database...")
            self._client = motor.motor_asyncio.AsyncIOMotorClient(Config.DATABASE_URL)
            self.db = self._client["StreamLinksDB"]
            self.collection = self.db["links"]
            print("✅ Database connection established.")
        else:
            self.db = None
            self.collection = None

    async def disconnect(self):
        """Database connection ko band karta hai."""
        if self._client:
            self._client.close()
            print("Database connection closed.")

    async def save_link(self, unique_id, message_id):
        if self.collection is not None:
            await self.collection.insert_one({'_id': unique_id, 'message_id': message_id})

    async def get_link(self, unique_id):
        if self.collection is not None:
            doc = await self.collection.find_one({'_id': unique_id})
            return doc.get('message_id') if doc else None
        return None

    async def get_stats(self):
        """Total link count aur MongoDB storage usage return karta hai."""
        if self.db is None:
            return None
        stats = await self.db.command("dbStats")
        count = await self.collection.count_documents({})
        return {
            "count": count,
            "data_size": stats.get("dataSize", 0),
            "storage_size": stats.get("storageSize", 0),
            "index_size": stats.get("indexSize", 0),
        }

    async def clean_all(self):
        """Saare saved links delete kar deta hai (database clean)."""
        if self.collection is not None:
            result = await self.collection.delete_many({})
            return result.deleted_count
        return 0

db = Database()
