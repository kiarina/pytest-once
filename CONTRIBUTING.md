# Contributing to pytest-once

Thank you for your interest in contributing to pytest-once! 🎉

## Development Setup

### Prerequisites

- [mise](https://mise.jdx.dev/) - Runtime and tool version manager
- Git

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/kiarina/pytest-once.git
   cd pytest-once
   ```

2. **Setup development environment**
   ```bash
   mise run setup
   ```
   This will:
   - Install Python 3.13 and uv via mise
   - Install all dependencies (including dev and test groups)

3. **Verify setup**
   ```bash
   mise run ci
   ```

## Development Workflow

### Available Tasks

Check available tasks:
```bash
mise tasks
```

Common tasks:
- `mise run` - Quick checks (format, lint-fix, typecheck, test)
- `mise run format` - Format code with ruff
- `mise run lint` - Lint code (ruff check + format check)
- `mise run lint-fix` - Auto-fix lint issues
- `mise run typecheck` - Type check with mypy
- `mise run test` - Run tests
- `mise run test --verbose` - Run tests with verbose output
- `mise run test --coverage` - Run tests with coverage report
- `mise run ci` - Run all CI checks (format, lint, typecheck, test, build)
- `mise run build` - Build package
- `mise run clean` - Clean build artifacts and cache files

### Making Changes

1. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code
   - Add tests for new functionality
   - Update documentation if needed

3. **Run checks locally**
   ```bash
   mise run ci
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```
   
   We follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `test:` - Test changes
   - `refactor:` - Code refactoring
   - `chore:` - Maintenance tasks

5. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style

- **Formatting**: We use `ruff format` (automatically applied)
- **Linting**: We use `ruff check` (see `.ruff.toml` for rules)
- **Type hints**: All code must be fully typed and pass `mypy --strict`

## Testing

- Write tests for all new functionality
- Ensure all tests pass: `mise run test`
- Test with xdist: `mise run test` (tests include xdist scenarios)
- Aim for high test coverage

### Test Structure

```python
# tests/test_your_feature.py
def test_your_feature(pytester):
    """Test description."""
    # Use pytester fixture for integration tests
    pytester.makeconftest("""
        # conftest.py content
    """)
    
    pytester.makepyfile("""
        # test file content
    """)
    
    result = pytester.runpytest("-q")
    result.assert_outcomes(passed=1)
```

## Documentation

- Update `README.md` for user-facing changes
- Update `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/)
- Add docstrings to all public APIs
- Update type hints

## Pull Request Process

1. Ensure all CI checks pass
2. Update documentation as needed
3. Add entry to `CHANGELOG.md` under `[Unreleased]`
4. Request review from maintainers
5. Address review feedback
6. Once approved, maintainers will merge your PR

## Release Process (for maintainers)

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`:
   - Move `[Unreleased]` changes to new version section
   - Add release date
   - Update version links at bottom
3. Commit changes: `git commit -m "chore: release v0.x.x"`
4. Create and push tag: `git tag v0.x.x && git push origin v0.x.x`
5. GitHub Actions will automatically:
   - Run CI checks
   - Build package
   - Publish to PyPI
   - Create GitHub Release

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Questions about contributing
- General discussions

## Code of Conduct

Be respectful and constructive in all interactions. We're here to build something useful together! 🚀

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
