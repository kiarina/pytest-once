# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-01-10

### Added
- Initial release of pytest-once
- `once_fixture` decorator for xdist-safe one-time setup
- File lock-based inter-process synchronization
- Support for Python 3.12+
- Comprehensive test suite with xdist validation
- Documentation and examples

### Features
- ✅ Setup-only execution (no teardown)
- ✅ xdist-safe: runs exactly once across all workers
- ✅ Idempotent setup pattern support
- ✅ Simple decorator-based API
- ✅ Type hints and mypy support

[Unreleased]: https://github.com/kiarina/pytest-once/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/kiarina/pytest-once/releases/tag/v0.1.0
