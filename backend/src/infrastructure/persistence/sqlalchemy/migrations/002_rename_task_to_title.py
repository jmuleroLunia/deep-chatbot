"""
Migration: Rename task column to title in plans table.

The old schema used 'task', new schema uses 'title' for consistency.
"""

import asyncio

from sqlalchemy import text

from ..base import async_engine


async def upgrade():
    """Rename task column to title."""
    print("🔄 Running migration: Rename task to title in plans table...")

    async with async_engine.begin() as conn:
        # SQLite doesn't support RENAME COLUMN directly in old versions
        # We need to: create new column, copy data, drop old column

        # Check if title column already exists
        result = await conn.execute(
            text("PRAGMA table_info(plans)")
        )
        columns = result.fetchall()
        column_names = [col[1] for col in columns]

        if "title" in column_names:
            print("✅ Column 'title' already exists, skipping migration")
            return

        # Add title column
        await conn.execute(
            text("ALTER TABLE plans ADD COLUMN title TEXT")
        )

        # Copy data from task to title
        await conn.execute(
            text("UPDATE plans SET title = task WHERE title IS NULL")
        )

        # Make title NOT NULL
        # SQLite doesn't support ALTER COLUMN, so we'll leave it nullable
        # but the ORM model enforces NOT NULL

        print("✅ Migration completed: task renamed to title")


async def main():
    """Run migration."""
    await upgrade()


if __name__ == "__main__":
    asyncio.run(main())
