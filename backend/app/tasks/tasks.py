"""Task utilities and background job runner."""

import logging
from typing import Callable, Optional
from datetime import datetime, time
import asyncio

logger = logging.getLogger(__name__)


class TaskRunner:
    """Background task runner."""

    _tasks = {}

    @classmethod
    def register(cls, name: str, func: Callable, interval_seconds: int):
        """Register a background task."""
        cls._tasks[name] = {
            "function": func,
            "interval": interval_seconds,
            "last_run": None
        }
        logger.info(f"Registered task: {name} (interval: {interval_seconds}s)")

    @classmethod
    async def run_all(cls):
        """Run all registered tasks."""
        while True:
            for name, task in cls._tasks.items():
                try:
                    # Check if it's time to run
                    if cls._should_run(task):
                        logger.info(f"Running task: {name}")
                        result = task["function"]()
                        task["last_run"] = datetime.utcnow()
                        logger.info(f"Task {name} completed: {result}")
                except Exception as e:
                    logger.error(f"Error running task {name}: {e}")
            
            # Check every minute
            await asyncio.sleep(60)

    @staticmethod
    def _should_run(task):
        """Check if task should run based on interval."""
        if task["last_run"] is None:
            return True
        
        elapsed = (datetime.utcnow() - task["last_run"]).total_seconds()
        return elapsed >= task["interval"]


def register_billing_tasks():
    """Register billing-related tasks."""
    from app.tasks.scheduler import BillingScheduler

    # Generate invoices daily at 2 AM (in seconds since midnight)
    TaskRunner.register(
        "generate_monthly_invoices",
        BillingScheduler.generate_monthly_invoices,
        interval_seconds=86400  # 24 hours
    )

    # Check overdue invoices every 6 hours
    TaskRunner.register(
        "mark_overdue_invoices",
        BillingScheduler.mark_overdue_invoices,
        interval_seconds=21600  # 6 hours
    )

    # Auto-renew subscriptions daily
    TaskRunner.register(
        "auto_renew_subscriptions",
        BillingScheduler.auto_renew_subscriptions,
        interval_seconds=86400  # 24 hours
    )

    # Send payment reminders daily
    TaskRunner.register(
        "send_payment_reminders",
        BillingScheduler.send_payment_reminders,
        interval_seconds=86400  # 24 hours
    )

    # Suspend overdue subscriptions every 12 hours
    TaskRunner.register(
        "suspend_overdue_subscriptions",
        BillingScheduler.suspend_overdue_subscriptions,
        interval_seconds=43200  # 12 hours
    )

    # Generate usage reports daily
    TaskRunner.register(
        "generate_usage_report",
        BillingScheduler.generate_usage_report,
        interval_seconds=86400  # 24 hours
    )
