from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDBClient:
    def __init__(self):
        self.client: AsyncIOMotorClient = None

    def connect(self):
        if not self.client:
            self.client = AsyncIOMotorClient(settings.MONGO_URI)
            print("Connected to MongoDB")

    def close(self):
        if self.client:
            self.client.close()
            print("Closed MongoDB connection")

    def get_database(self, db_name: str = None):
        if db_name:
            return self.client[db_name]
        return self.client[settings.MASTER_DB_NAME]

db_client = MongoDBClient()

async def get_master_db():
    return db_client.get_database(settings.MASTER_DB_NAME)

async def get_tenant_collection_name(org_name: str) -> str:
    # Safely format collection name
    return f"org_{org_name.lower().replace(' ', '_')}"
