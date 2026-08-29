"""Migration 狀態檢查。

模型改了卻忘了產生 migration，是 Django 專案最常見、也最容易在部署當下才炸開的
失誤：本機因為資料庫早就有那個欄位所以完全正常，正式環境套用時才發現對不上。
"""
import io

import pytest
from django.core.management import call_command
from django.db.migrations.loader import MigrationLoader

pytestmark = pytest.mark.django_db


def test_no_model_changes_are_missing_a_migration():
    """`makemigrations --check` 必須是乾淨的。"""
    output = io.StringIO()
    try:
        call_command("makemigrations", "--check", "--dry-run", stdout=output, verbosity=1)
    except SystemExit as exc:  # --check 在有變更時以非零狀態結束
        pytest.fail(
            "偵測到尚未產生 migration 的模型變更：\n"
            f"{output.getvalue()}\n"
            "請執行 `python manage.py makemigrations` 並提交產生的檔案。"
            f"（SystemExit: {exc.code}）"
        )


def test_migration_graph_has_no_conflicts():
    """每個 app 只能有一個 migration 葉節點。

    兩個人同時從同一個 migration 分出新檔案就會產生分岔；分岔在合併當下不會報錯，
    要到有人執行 migrate 才會失敗。
    """
    from django.db import connection

    loader = MigrationLoader(connection)
    conflicts = loader.detect_conflicts()
    assert not conflicts, (
        f"migration 出現分岔（同一 app 有多個葉節點）：{conflicts}\n"
        "請執行 `python manage.py makemigrations --merge` 解決。"
    )


def test_all_migrations_apply_to_an_empty_database():
    """整份 migration 能從零套用到底。

    測試資料庫本來就是這樣建起來的，所以這條真正的價值在於：它讓「migration 壞掉」
    以一個名字清楚的失敗呈現，而不是整份測試在 session 啟動階段就以難懂的錯誤炸掉。
    """
    from django.db import connection

    loader = MigrationLoader(connection)
    assert loader.graph.leaf_nodes(), "找不到任何 migration，狀態不正常。"
