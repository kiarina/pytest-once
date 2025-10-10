# pytest-once

[![CI](https://github.com/kiarina/pytest-once/actions/workflows/ci.yml/badge.svg)](https://github.com/kiarina/pytest-once/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/pytest-once.svg)](https://badge.fury.io/py/pytest-once)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-once.svg)](https://pypi.org/project/pytest-once/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**xdist-safe** な「一度だけ実行」用の pytest フィクスチャ・デコレータです。複数ワーカー（`pytest-xdist`）でも、**セットアップは一回だけ**実行されます。

- ✅ `filelock` によるプロセス間ロックで **二重実行を防止**
- ✅ xdist なしでもそのまま動作
- ✅ API は **デコレータ 1 つ**だけ
- ✅ シンプルで理解しやすい（teardown なし）

## インストール

```bash
pip install pytest-once
# 併せて xdist を使うなら
pip install pytest-xdist
```

## 使い方（クイック）

```python
from pytest_once import once_fixture
import pytest

@once_fixture(autouse=True, scope="session")
def bootstrap_db():
    cleanup_old_containers()  # べき等なクリーンアップ
    start_db_container()

@pytest.fixture
def client(bootstrap_db):  # ← 依存を明示
    return create_client()

@once_fixture(autouse=True, scope="session")
def seed_data():
    load_seed_dataset()

# 必要に応じて明示的にフィクスチャ名を指定することも可能
@once_fixture("db", autouse=True, scope="session")
def bootstrap_database():
    start_db_container()
```

* 値（クライアント等）を返したい場合は、**別の通常フィクスチャで依存**させてください（このデコレータは値を返しません）。
* **べき等な setup** を推奨：setup 内で前回の残骸をクリーンアップすることで、再実行時も安全に動作します。

## 動作保証の要点

* `setup` は **一度だけ** 実行されます（ロック＋マーカーで制御）。
* **teardown はサポートしていません**。以下の戦略を推奨します：
  * **CI 環境**: テスト終了後に環境ごと破棄される（自動クリーンアップ）
  * **Local 環境**: 次回実行時の setup でクリーンアップ（べき等な setup）
  * **Docker コンテナ**: `docker-compose down` などの外部ツールで管理
  * **一時ファイル**: pytest の `tmp_path` が自動的にクリーンアップ

## Teardown が必要な場合の対処法

### パターン 1: べき等な setup（推奨）

```python
@once_fixture("db_container", autouse=True, scope="session")
def db_container():
    # 前回の残骸をクリーンアップ
    stop_and_remove_old_containers()
    # 新しいコンテナを起動
    start_db_container()
```

### パターン 2: 外部ツールで管理

```bash
# テスト実行
pytest -n 4

# テスト終了後にクリーンアップ
docker-compose down
```

### パターン 3: CI の自動クリーンアップ

```yaml
# GitHub Actions の例
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest -n 4
      # ジョブ終了時に自動的に環境が破棄される
```

## パラメータ

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

* **fixture_name**: 登録されるフィクスチャ名（依存時に `def f(fixture_name): ...` の形で使います）。`None` の場合はデコレートされた関数名を使用します（デフォルト）。
* **scope** / **autouse**: 通常の pytest と同じ意味
* **lock_timeout**: ファイルロック取得のタイムアウト秒
* **namespace**: 共有テンポラリ直下に作られる管理ディレクトリ名

## 既知の制約

* このデコレータ自体は **値を返しません**。共有したい値は別フィクスチャで提供してください。
* **generator 関数（`yield` を含む）はサポートしていません**。使用すると `TypeError` が発生します。
* 異常終了（強制 kill 等）時はマーカーが残る可能性があります。再実行時に自動回復しますが、必要に応じて `namespace` を切り替えてください。

## ライセンス

MIT License © Aki
