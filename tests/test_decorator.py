# NOTE: These tests use the built-in Pytester fixture to spawn sub-process
# pytest runs, including an xdist run. They validate that setup happens
# exactly once across workers.


def test_setup_only_runs_once_no_xdist(pytester):
    """Setup-only should run exactly once without xdist."""
    pytester.makeconftest(
        r"""
from pathlib import Path
from pytest_once import once_fixture

COUNTER = Path("counter_setup.txt")

@once_fixture(autouse=True, scope="session")
def seed_data():
    if COUNTER.exists():
        try:
            n = int(COUNTER.read_text().strip())
        except Exception:
            n = 0
        COUNTER.write_text(str(n + 1))
    else:
        COUNTER.write_text("1")
"""
    )

    pytester.makepyfile(
        **{
            "test_a.py": """
def test_a1():
    assert True

def test_a2():
    assert True
""",
            "test_b.py": """
def test_b1():
    assert True

def test_b2():
    assert True
""",
        }
    )

    result = pytester.runpytest("-q")
    result.assert_outcomes(passed=4)

    cnt_path = pytester.path.joinpath("counter_setup.txt")
    assert cnt_path.exists(), "setup should have created the counter file"
    assert cnt_path.read_text().strip() == "1", "setup must run exactly once"


def test_setup_runs_once_with_xdist(pytester):
    """With xdist, setup should run exactly once across all workers."""
    pytester.makeconftest(
        r"""
from pathlib import Path
from pytest_once import once_fixture

SETUP = Path("setup_count.txt")
RESOURCE = Path("resource_alive.flag")

@once_fixture(autouse=True, scope="session")
def bootstrap():
    # setup: create resource + count
    if SETUP.exists():
        try:
            n = int(SETUP.read_text().strip())
        except Exception:
            n = 0
        SETUP.write_text(str(n + 1))
    else:
        SETUP.write_text("1")
    RESOURCE.write_text("alive")
"""
    )

    pytester.makepyfile(
        **{
            "test_x.py": """
from pathlib import Path

def test_x1():
    assert Path('resource_alive.flag').exists()

def test_x2():
    assert Path('resource_alive.flag').read_text().strip() == 'alive'
""",
            "test_y.py": """
from pathlib import Path

def test_y1():
    assert Path('resource_alive.flag').exists()

def test_y2():
    assert Path('resource_alive.flag').read_text().strip() == 'alive'
""",
        }
    )

    # Run with two workers
    result = pytester.runpytest("-q", "-n", "2")
    result.assert_outcomes(passed=4)

    # After the run, setup must be exactly 1
    setup_cnt = pytester.path.joinpath("setup_count.txt")
    resource_flag = pytester.path.joinpath("resource_alive.flag")

    assert setup_cnt.exists() and setup_cnt.read_text().strip() == "1"
    # Resource remains (no teardown)
    assert resource_flag.exists()


def test_multiple_modules_share_same_once_fixture(pytester):
    """Two modules using the same once fixture should still run only-once setup."""
    pytester.makeconftest(
        r"""
from pathlib import Path
from pytest_once import once_fixture

COUNT = Path("multi_setup.txt")

@once_fixture("global_init", autouse=True, scope="session")
def global_init():
    if COUNT.exists():
        try:
            n = int(COUNT.read_text().strip())
        except Exception:
            n = 0
        COUNT.write_text(str(n + 1))
    else:
        COUNT.write_text("1")
"""
    )

    pytester.makepyfile(
        **{
            "test_m1.py": """
def test_m1():
    assert True
""",
            "test_m2.py": """
def test_m2():
    assert True
""",
        }
    )

    result = pytester.runpytest("-q")
    result.assert_outcomes(passed=2)

    cnt = pytester.path.joinpath("multi_setup.txt")
    assert cnt.exists() and cnt.read_text().strip() == "1"


def test_idempotent_setup_pattern(pytester):
    """Test idempotent setup pattern (cleanup in setup)."""
    pytester.makeconftest(
        r"""
from pathlib import Path
from pytest_once import once_fixture

RESOURCE = Path("resource.txt")
SETUP_COUNT = Path("setup_count.txt")

@once_fixture(autouse=True, scope="session")
def idempotent_resource():
    # Cleanup old resource (idempotent)
    if RESOURCE.exists():
        RESOURCE.unlink()

    # Track setup count
    if SETUP_COUNT.exists():
        try:
            n = int(SETUP_COUNT.read_text().strip())
        except Exception:
            n = 0
        SETUP_COUNT.write_text(str(n + 1))
    else:
        SETUP_COUNT.write_text("1")

    # Create new resource
    RESOURCE.write_text("fresh")
"""
    )

    pytester.makepyfile(
        **{
            "test_resource.py": """
from pathlib import Path

def test_resource_exists():
    assert Path('resource.txt').exists()

def test_resource_content():
    assert Path('resource.txt').read_text() == 'fresh'
""",
        }
    )

    result = pytester.runpytest("-q")
    result.assert_outcomes(passed=2)

    setup_cnt = pytester.path.joinpath("setup_count.txt")
    assert setup_cnt.exists() and setup_cnt.read_text().strip() == "1"


def test_generator_function_raises_error(pytester):
    """Generator functions (with yield) should raise TypeError."""
    pytester.makeconftest(
        r"""
from pytest_once import once_fixture

@once_fixture("bad_fixture", autouse=True, scope="session")
def bad_fixture():
    print("setup")
    yield
    print("teardown")
"""
    )

    pytester.makepyfile(
        """
def test_dummy():
    assert True
"""
    )

    result = pytester.runpytest("-q")
    # Should fail during collection due to TypeError
    assert result.ret != 0
    # Error appears in stderr during conftest import
    result.stderr.fnmatch_lines(["*TypeError*does not support generator functions*"])


def test_function_with_parameters_raises_error(pytester):
    """Functions with parameters should raise TypeError."""
    pytester.makeconftest(
        r"""
from pytest_once import once_fixture

@once_fixture("bad_fixture", autouse=True, scope="session")
def bad_fixture(some_param):
    print("setup")
"""
    )

    pytester.makepyfile(
        """
def test_dummy():
    assert True
"""
    )

    result = pytester.runpytest("-q")
    # Should fail during collection due to TypeError
    assert result.ret != 0
    # Error appears in stderr during conftest import
    result.stderr.fnmatch_lines(["*TypeError*must take no parameters*"])


def test_explicit_fixture_name(pytester):
    """Test that explicit fixture_name parameter works correctly."""
    pytester.makeconftest(
        r"""
from pathlib import Path
from pytest_once import once_fixture

COUNTER = Path("explicit_name_counter.txt")

@once_fixture("custom_name", autouse=True, scope="session")
def my_setup_function():
    if COUNTER.exists():
        try:
            n = int(COUNTER.read_text().strip())
        except Exception:
            n = 0
        COUNTER.write_text(str(n + 1))
    else:
        COUNTER.write_text("1")
"""
    )

    pytester.makepyfile(
        """
def test_explicit_name():
    assert True
"""
    )

    result = pytester.runpytest("-q")
    result.assert_outcomes(passed=1)

    cnt_path = pytester.path.joinpath("explicit_name_counter.txt")
    assert cnt_path.exists(), "setup should have created the counter file"
    assert cnt_path.read_text().strip() == "1", "setup must run exactly once"
