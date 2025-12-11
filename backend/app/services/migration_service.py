from app.db.client import get_master_db, get_tenant_collection_name
from app.db.master_repo import master_repo
from fastapi import HTTPException
from datetime import datetime

class MigrationService:
    @staticmethod
    async def perform_migration(old_org_name: str, new_org_name: str, org_id: str):
        db = await get_master_db()
        
        old_collection_name = await get_tenant_collection_name(old_org_name)
        new_collection_name = await get_tenant_collection_name(new_org_name)

        if old_collection_name == new_collection_name:
            return # No change needed

        # 1. Create New Collection (implicitly created on write, but good to be explicit or check checks)
        # 2. Bulk Copy Documents
        old_collection = db[old_collection_name]
        new_collection = db[new_collection_name]

        # Use aggregation $out or manual copy? 
        # Atlas restricts $out across DBs but checking if single DB approach is used (yes per PRD).
        # However, manual batch copy is safer for "migration" with verification logic.
        # For simplicity and "single DB", we can try $merge or simple iterating.
        
        # Using simple iteration for robustness in this example (for large datasets, use cursor and bulk_write)
        # Note: In production with millions of docs, use a background worker or database tools.
        
        docs_to_copy = []
        async for doc in old_collection.find({}):
            docs_to_copy.append(doc)
            
        if docs_to_copy:
            await new_collection.insert_many(docs_to_copy)

        # 3. Verify Counts
        count_old = await old_collection.count_documents({})
        count_new = await new_collection.count_documents({})

        if count_old != count_new:
            # Rollback: Drop new collection
            await new_collection.drop()
            raise HTTPException(status_code=500, detail="Migration verification failed: Document counts do not match.")

        # 4. Update Organization Metadata
        await master_repo.update_org_metadata(
            org_id, 
            {
                "organization_name": new_org_name,
                "collection_name": new_collection_name,
                "connection.collection_name": new_collection_name,
                "updated_at": datetime.utcnow()
            }
        )

        # 5. Drop Old Collection (or soft delete/rename for backup)
        # Per PRD: "Drop old collection only after successful verification or keep backup"
        # We will drop for now to keep it clean, but consider renaming to _backup in p2
        await old_collection.drop()
        
        return True
