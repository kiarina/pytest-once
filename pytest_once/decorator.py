import inspect
from collections.abc import Callable
from pathlib import Path
from typing import Literal

import pytest
from filelock import FileLock, Timeout
from pytest import FixtureRequest, TempPathFactory

# Type aliases for clarity
_Scope = Literal["session", "module", "class", "function"]
_SetupFunc = Callable[[], None]


def once_fixture(
    fixture_name: str | None = None,
    *,
    scope: _Scope = "session",
    autouse: bool = False,
    lock_timeout: float = 60.0,
    namespace: str = "pytest-once",
) -> Callable[[_SetupFunc], Callable[[TempPathFactory, FixtureRequest], None]]:
    """
    Run one-time setup exactly once across all xdist workers (xdist-safe).

    The decorated function must:
      - take no parameters
      - be a normal function (not a generator)
      - perform idempotent setup (safe to run multiple times if needed)

    Examples:
        # Use function name as fixture name (recommended)
        @once_fixture(autouse=True, scope="session")
        def bootstrap_db():
            cleanup_old_containers()  # idempotent cleanup
            start_db_container()

        @once_fixture(autouse=True, scope="session")
        def seed_data():
            load_seed_dataset()

        # Or explicitly specify fixture name if needed
        @once_fixture("db", autouse=True, scope="session")
        def bootstrap_db():
            start_db_container()

    Notes / Guarantees:
      - Setup is executed exactly once across workers, guarded by a file lock.
      - No teardown support: use idempotent setup or external cleanup
        (CI, docker-compose, etc.)
      - This fixture returns no meaningful value. If you need a resource/client,
        define a separate normal fixture that depends on this one.

    Teardown Strategy:
      - CI environments: Environment is destroyed after tests (automatic cleanup)
      - Local development: Next run's setup performs cleanup (idempotent setup)
      - Docker containers: Use `docker-compose down` or similar external tools
      - Temporary files: pytest's tmp_path cleanup handles this automatically

    Parameters:
      fixture_name:   Name of the pytest fixture that will be exposed/registered.
                      If None (default), uses the decorated function's name.
      scope:          Pytest fixture scope (default "session").
      autouse:        Whether to autouse the fixture.
      lock_timeout:   Seconds to wait when acquiring the file lock.
      namespace:      Directory name under base tmp for bookkeeping files.
    """

    def decorator(
        setup_func: _SetupFunc,
    ) -> Callable[[TempPathFactory, FixtureRequest], None]:
        # Use function name if fixture_name is not provided
        actual_fixture_name = (
            fixture_name if fixture_name is not None else setup_func.__name__
        )

        # Enforce: function must take no parameters
        sig = inspect.signature(setup_func)
        if len(sig.parameters) != 0:
            raise TypeError(
                "once_fixture target must take no parameters. "
                "Define dependencies in a separate fixture and depend on this one."
            )

        # Enforce: function must not be a generator
        if inspect.isgeneratorfunction(setup_func):
            raise TypeError(
                "once_fixture does not support generator functions (yield). "
                "Use idempotent setup or external cleanup instead. "
                "See documentation for teardown strategies."
            )

        @pytest.fixture(scope=scope, autouse=autouse, name=actual_fixture_name)
        def _once_fixture(
            tmp_path_factory: TempPathFactory, request: FixtureRequest
        ) -> None:
            # Shared directory across workers:
            # .../tmp/pytest-of-.../<run>/pytest-once/<fixture_name>/
            base_root = tmp_path_factory.getbasetemp().parent
            base: Path = base_root / namespace / actual_fixture_name
            base.mkdir(parents=True, exist_ok=True)

            marker = base / "ready"  # setup completed marker
            lock_path = base / "lock"  # file lock for atomic ops
            lock = FileLock(str(lock_path))

            # --- SETUP (run-once with lock) ---
            if not marker.exists():
                try:
                    with lock.acquire(timeout=lock_timeout):
                        # Double-check after acquiring lock
                        if not marker.exists():
                            setup_func()  # Run setup exactly once
                            marker.touch()
                except Timeout as e:
                    raise TimeoutError(
                        f"Timed out acquiring lock for once_fixture "
                        f"'{actual_fixture_name}'. "
                        "A previous worker may have crashed while holding the lock."
                    ) from e

            # Fixture has no return value by design
            return None

        return _once_fixture

    return decorator
