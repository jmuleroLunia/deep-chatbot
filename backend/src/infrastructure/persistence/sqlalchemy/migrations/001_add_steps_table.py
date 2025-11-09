"""
Migration: Add steps table.

The old schema stored steps as JSON in the plans table.
This migration creates a separate steps table for proper normalization.
"""

import asyncio

from sqlalchemy import text

from ..base import async_engine


async def upgrade():
    """Create steps table."""
    print("🔄 Running migration: Add steps table...")

    async with async_engine.begin() as conn:
        # Create steps table
        await conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_id INTEGER NOT NULL,
                    step_number INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    completed BOOLEAN NOT NULL DEFAULT 0,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (plan_id) REFERENCES plans(id) ON DELETE CASCADE
                )
                """
            )
        )

        # Add index on plan_id
        await conn.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS idx_steps_plan_id ON steps(plan_id)
                """
            )
        )

        # Migrate existing plans with JSON steps to new table
        # First, get all plans with steps
        result = await conn.execute(
            text("SELECT id, steps FROM plans WHERE steps IS NOT NULL")
        )
        plans_with_steps = result.fetchall()

        import json

        for plan_id, steps_json in plans_with_steps:
            if not steps_json:
                continue

            try:
                steps = json.loads(steps_json)
                if not isinstance(steps, list):
                    continue

                # Insert steps into new table
                for idx, step in enumerate(steps, start=1):
                    if isinstance(step, dict):
                        description = step.get("description", "")
                        completed = step.get("completed", False)
                        completed_at = step.get("completed_at")

                        await conn.execute(
                            text(
                                """
                                INSERT INTO steps (plan_id, step_number, description, completed, completed_at)
                                VALUES (:plan_id, :step_number, :description, :completed, :completed_at)
                                """
                            ),
                            {
                                "plan_id": plan_id,
                                "step_number": idx,
                                "description": description,
                                "completed": completed,
                                "completed_at": completed_at,
                            },
                        )

            except Exception as e:
                print(f"⚠️ Warning: Failed to migrate steps for plan {plan_id}: {e}")

        # Remove steps column from plans table (optional, for cleanup)
        # Note: SQLite doesn't support DROP COLUMN, so we'll leave it

        print("✅ Migration completed: Steps table created and data migrated")


async def downgrade():
    """Remove steps table (for rollback)."""
    print("🔄 Rolling back migration: Remove steps table...")

    async with async_engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS steps"))

    print("✅ Rollback completed: Steps table removed")


async def main():
    """Run migration."""
    await upgrade()


if __name__ == "__main__":
    asyncio.run(main())
