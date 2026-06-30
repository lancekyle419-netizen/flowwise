"""Database migration utilities."""

import subprocess
import sys
from pathlib import Path

from app.config import settings


def run_migrations():
    """Run database migrations."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Migration failed: {result.stderr}")
            return False
        print("Migrations completed successfully")
        return True
    except Exception as e:
        print(f"Error running migrations: {e}")
        return False


def create_migration(message: str):
    """Create a new migration."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "revision", "--autogenerate", "-m", message],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Migration creation failed: {result.stderr}")
            return False
        print(f"Migration created: {result.stdout}")
        return True
    except Exception as e:
        print(f"Error creating migration: {e}")
        return False
