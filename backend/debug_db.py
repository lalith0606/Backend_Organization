import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import sys

async def check_connection():
    print(f"Attempting to connect to: {settings.MONGO_URI}")
    
    try:
        client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
        # Force a command to verify connection
        await client.admin.command('ping')
        print("SUCCESS: Connected to MongoDB successfully!")
    except Exception as e:
        print(f"ERROR: Failed to connect to MongoDB.")
        print(f"Details: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_connection())
