# pytest-once

[![CI](https://github.com/kiarina/pytest-once/actions/workflows/ci.yml/badge.svg)](https://github.com/kiarina/pytest-once/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/pytest-once.svg)](https://badge.fury.io/py/pytest-once)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-once.svg)](https://pypi.org/project/pytest-once/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**xdist-safe** "run once" pytest fixture decorator. Setup runs **exactly once** even with multiple workers (`pytest-xdist`).

## Features

- ✅ **Prevents duplicate execution** with file lock-based inter-process synchronization
- ✅ **Works with or without xdist** - seamless integration
- ✅ **Simple API** - just one decorator
- ✅ **Type-safe** - full type hints and mypy support
- ✅ **No teardown complexity** - encourages idempotent setup patterns

## Installation

```bash
pip install pytest-once

# If using with xdist
pip install pytest-xdist
```

## Quick Start

```python
from pytest_once import once_fixture
import pytest

@once_fixture(autouse=True, scope="session")
def bootstrap_db():
    """Setup database container - runs once across all workers."""
    cleanup_old_containers()  # Idempotent cleanup
    start_db_container()

@pytest.fixture
def client(bootstrap_db):  # Explicit dependency
    """Create a client that depends on the database."""
    return create_client()

@once_fixture(autouse=True, scope="session")
def seed_data():
    """Load seed data - runs once after bootstrap_db."""
    load_seed_dataset()

# You can also explicitly specify the fixture name
@once_fixture("db", autouse=True, scope="session")
def bootstrap_database():
    """Alternative: explicit fixture name."""
    start_db_container()
```

### Key Points

- **Return values**: This decorator doesn't return values. Use a separate regular fixture that depends on the once_fixture if you need to share resources.
- **Idempotent setup recommended**: Clean up previous runs within setup to ensure safe re-execution.

## How It Works

When running tests in parallel with `pytest-xdist`, normal fixtures run independently in each worker process. Even with `scope="session"`, setup runs multiple times (once per worker), causing:

- ⚠️ Resource waste (e.g., multiple identical containers)
- ⚠️ Port conflicts and runtime errors
- ⚠️ Increased test execution time

`pytest-once` uses **file lock-based synchronization** to ensure setup runs exactly once:

1. First worker acquires lock and runs setup
2. Other workers wait for the lock
3. After setup completes, a marker file is created
4. Subsequent workers see the marker and skip setup

## Teardown Strategy

This decorator **does not support teardown**. Instead, we recommend these patterns:

### Pattern 1: Idempotent Setup (Recommended)

Clean up in the setup phase to ensure safe re-runs:

```python
@once_fixture("db_container", autouse=True, scope="session")
def db_container():
    """Setup with built-in cleanup."""
    # Clean up any previous containers
    stop_and_remove_old_containers()

    # Start fresh container
    start_db_container()
```

### Pattern 2: External Cleanup Tools

Use external tools for cleanup:

```bash
# Run tests
pytest -n 4

# Clean up after tests
docker-compose down
```

### Pattern 3: CI Auto-Cleanup

Let CI environments handle cleanup automatically:

```yaml
# GitHub Actions example
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: pytest -n 4
      # Environment is automatically destroyed after job completes
```

### Pattern 4: Temporary Files

Use pytest's built-in temporary directory fixtures:

```python
@pytest.fixture(scope="session")
def temp_data(tmp_path_factory):
    """Temporary files are automatically cleaned up."""
    data_dir = tmp_path_factory.mktemp("data")
    # pytest cleans this up automatically
    return data_dir
```

## API Reference

```python
once_fixture(
    fixture_name: str | None = None,
    *,
    scope: str = "session",
    autouse: bool = False,
    lock_timeout: float = 60.0,
    namespace: str = "pytest-once",
)
```

### Parameters

- **fixture_name** (optional): Name of the registered fixture. If `None`, uses the decorated function's name. Use this when you need to reference the fixture in test dependencies.

- **scope**: Pytest fixture scope. Default: `"session"`
  - `"session"`: Once per test session (recommended)
  - `"module"`: Once per test module
  - `"class"`: Once per test class
  - `"function"`: Once per test function

- **autouse**: Whether to automatically use this fixture. Default: `False`
  - `True`: Runs automatically without explicit dependency
  - `False`: Must be explicitly referenced in test parameters

- **lock_timeout**: Timeout in seconds for acquiring the file lock. Default: `60.0`
  - Increase if setup takes longer than 60 seconds
  - Decrease for faster failure detection

- **namespace**: Directory name under pytest's temp directory for lock files. Default: `"pytest-once"`
  - Change if you need to isolate different test suites

## Advanced Examples

### Multiple Once Fixtures with Dependencies

```python
@once_fixture(autouse=True, scope="session")
def setup_infrastructure():
    """First: setup infrastructure."""
    start_docker_network()
    start_database()

@once_fixture(autouse=True, scope="session")
def setup_data(setup_infrastructure):
    """Second: setup data (depends on infrastructure)."""
    migrate_database()
    load_seed_data()

@pytest.fixture
def api_client(setup_data):
    """Regular fixture that depends on once_fixture."""
    return APIClient()
```

### Explicit Fixture Names

```python
@once_fixture("db", autouse=True, scope="session")
def bootstrap_database():
    """Fixture registered as 'db'."""
    start_db_container()

@pytest.fixture
def db_client(db):  # Reference by explicit name
    """Create client that depends on 'db' fixture."""
    return create_db_client()
```

### Custom Lock Timeout

```python
@once_fixture(autouse=True, scope="session", lock_timeout=300.0)
def slow_setup():
    """Setup that takes up to 5 minutes."""
    download_large_dataset()
    process_data()
```

## Known Limitations

1. **No return values**: The decorator doesn't return values. Create a separate regular fixture if you need to share resources:

   ```python
   @once_fixture("db_setup", autouse=True, scope="session")
   def db_setup():
       start_database()

   @pytest.fixture
   def db_connection(db_setup):
       """Regular fixture that returns a connection."""
       return create_connection()
   ```

2. **No generator functions**: Functions with `yield` are not supported and will raise `TypeError`:

   ```python
   # ❌ This will raise TypeError
   @once_fixture(autouse=True, scope="session")
   def bad_fixture():
       setup()
       yield  # Not supported!
       teardown()
   ```

3. **Crash recovery**: If a worker crashes while holding the lock, the marker file may be left behind. The next run will automatically recover, but you can also manually delete the lock directory or change the `namespace` parameter.

## Troubleshooting

### Lock Timeout Errors

If you see timeout errors:

```python
TimeoutError: Timed out acquiring lock for once_fixture 'my_fixture'
```

**Solutions:**
- Increase `lock_timeout` parameter
- Check if a previous worker crashed (restart pytest)
- Manually clean up lock files in pytest's temp directory

### Setup Running Multiple Times

If setup runs more than once:

1. Verify you're using `scope="session"`
2. Check that `autouse=True` or the fixture is properly referenced
3. Ensure the fixture name is unique across your test suite

### Import Errors

If you see import errors:

```python
ImportError: cannot import name 'once_fixture'
```

**Solution:** Ensure pytest-once is installed:
```bash
pip install pytest-once
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License © 2025 kiarina

## Links

- **Documentation**: [GitHub README](https://github.com/kiarina/pytest-once#readme)
- **Source Code**: [GitHub Repository](https://github.com/kiarina/pytest-once)
- **Issue Tracker**: [GitHub Issues](https://github.com/kiarina/pytest-once/issues)
- **Changelog**: [CHANGELOG.md](https://github.com/kiarina/pytest-once/blob/main/CHANGELOG.md)
- **PyPI**: [pytest-once](https://pypi.org/project/pytest-once/)
