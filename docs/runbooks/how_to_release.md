---
title: How to Release
description: Explains how to release pytest-once to PyPI.
---

This guide explains the release procedure using version 0.1.0 as an example.

## v0.1.0 Release Procedure

### 1. Update Version
```sh
# Update all packages to version 0.1.0
mise run version 0.1.0
```

### 2. Update CHANGELOG
Review and update the `CHANGELOG.md` files in the root and each package.

First, add the update details to the `Unreleased` section of the following `CHANGELOG.md` files:
- Root `CHANGELOG.md`: Summary of changes for all packages (one line per change)
- `packages/kiarina/CHANGELOG.md`: Same content as root for the kiarina meta-package
- `packages/<package-name>/CHANGELOG.md`: Detailed changes for each package

Next, run the following mise task to replace the `Unreleased` section in the CHANGELOG with the `v0.1.0` section:
```sh
mise run update-changelog 0.1.0
```
This task automatically adds `No changes` entries for packages without updates.

### 3. Review Changes
```sh
# Review changed files
git diff
```

### 4. Run CI Checks
```sh
# Ensure all CI checks pass
mise run ci
```

### 5. Commit, Tag, and Push
```sh
# Commit changes
git add .
git commit -m "chore: bump version to 0.1.0"

# Create annotated tag
git tag -s v0.1.0 -m "Release v0.1.0"

# Push with tags
git push --tags
```

## Automated Processes

When you push a tag, the `.github/workflows/release.yml` workflow in GitHub Actions automatically executes the following processes:

1. **CI Checks**: Runs format, lint, typecheck, test, and build
2. **GitHub Release**: Automatically creates a GitHub Release with release notes
3. **PyPI Publication**: Publishes all packages to PyPI (if `PYPI_API_TOKEN` is configured)
