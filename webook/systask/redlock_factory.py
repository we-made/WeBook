from django.conf import settings
import redlock


def get_redlock_factory() -> redlock.RedLockFactory:
    """Get a RedLockFactory instance for distributed locking.

    Returns:
        redlock.RedLockFactory: A RedLockFactory instance.
    """
    return redlock.RedLockFactory(
        connection_details=[
            {"host": settings.REDIS_URL.replace("redis://", "").split(":")[0]}
        ]
    )
