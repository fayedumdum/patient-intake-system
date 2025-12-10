from app.db.base import Base, async_engine

async def async_init_db():
    """
    Asynchronously creates all tables defined in Base.metadata if they don't exist.
    """
    # Use 'async with async_engine.begin() as conn:' for DDL operations (like create_all)
    async with async_engine.begin() as conn:
        # conn.run_sync allows calling synchronous DDL operations within an async context
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully.")